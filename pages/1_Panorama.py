# -*- coding: utf-8 -*-
"""
Módulo 1: Panorama del Sistema
Visión general del sistema bancario ecuatoriano.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))

from utils.data_loader import cargar_balance, obtener_fechas_disponibles
from utils.charts import (
    render_kpi_card,
    crear_ranking_barras,
    crear_treemap,
    crear_linea_temporal,
    crear_gauge,
    COLORES,
)
from config.indicator_mapping import CODIGOS_BALANCE, ETIQUETAS_BALANCE

# =============================================================================
# CONFIGURACION
# =============================================================================

st.set_page_config(
    page_title="Panorama | Radar Bancario",
    page_icon="📊",
    layout="wide",
)

# =============================================================================
# FUNCIONES DE CALCULO
# =============================================================================

@st.cache_data
def calcular_metricas_sistema(df: pd.DataFrame, fecha) -> dict:
    """Calcula metricas agregadas del sistema para una fecha."""
    df_fecha = df[df['fecha'] == fecha]

    metricas = {}

    # Total Activos (Codigo 1)
    activos = df_fecha[df_fecha['codigo'] == CODIGOS_BALANCE['activo_total']]
    metricas['total_activos'] = activos['valor'].sum() / 1000 if not activos.empty else 0

    # Cartera de Creditos (Codigo 14)
    cartera = df_fecha[df_fecha['codigo'] == CODIGOS_BALANCE['cartera_creditos']]
    metricas['total_cartera'] = cartera['valor'].sum() / 1000 if not cartera.empty else 0

    # Depositos del Publico (Codigo 21)
    depositos = df_fecha[df_fecha['codigo'] == CODIGOS_BALANCE['obligaciones_publico']]
    metricas['total_depositos'] = depositos['valor'].sum() / 1000 if not depositos.empty else 0

    # Patrimonio (Codigo 3)
    patrimonio = df_fecha[df_fecha['codigo'] == CODIGOS_BALANCE['patrimonio']]
    metricas['total_patrimonio'] = patrimonio['valor'].sum() / 1000 if not patrimonio.empty else 0

    # Fondos Disponibles (Codigo 11)
    fondos = df_fecha[df_fecha['codigo'] == CODIGOS_BALANCE['fondos_disponibles']]
    metricas['fondos_disponibles'] = fondos['valor'].sum() / 1000 if not fondos.empty else 0

    # Numero de bancos
    metricas['num_bancos'] = df_fecha['banco'].nunique()

    return metricas


@st.cache_data
def obtener_ranking_bancos(df: pd.DataFrame, fecha, codigo: str, top_n: int = 10) -> pd.DataFrame:
    """Obtiene ranking de bancos por cuenta especifica."""
    df_fecha = df[(df['fecha'] == fecha) & (df['codigo'] == codigo)]

    if df_fecha.empty:
        return pd.DataFrame()

    ranking = df_fecha[['banco', 'valor']].copy()
    ranking['valor_millones'] = ranking['valor'] / 1000
    ranking = ranking.sort_values('valor', ascending=False).head(top_n)

    return ranking


@st.cache_data
def calcular_concentracion_hhi(df: pd.DataFrame, fecha) -> tuple:
    """Calcula indice de concentracion HHI."""
    ranking = obtener_ranking_bancos(df, fecha, CODIGOS_BALANCE['activo_total'], top_n=50)

    if ranking.empty:
        return 0, pd.DataFrame()

    total = ranking['valor'].sum()
    ranking['participacion'] = (ranking['valor'] / total) * 100
    ranking['participacion_sq'] = ranking['participacion'] ** 2

    hhi = ranking['participacion_sq'].sum()

    return hhi, ranking


@st.cache_data
def obtener_serie_temporal(df: pd.DataFrame, codigo: str) -> pd.DataFrame:
    """Obtiene serie temporal agregada del sistema para una cuenta."""
    df_cuenta = df[(df['codigo'] == codigo)]

    serie = df_cuenta.groupby('fecha')['valor'].sum().reset_index()
    serie['valor_millones'] = serie['valor'] / 1000
    serie = serie.sort_values('fecha')

    return serie


@st.cache_data
def obtener_datos_treemap_jerarquico(df: pd.DataFrame, fecha, tipo='activos') -> pd.DataFrame:
    """Prepara datos jerarquicos para treemap con drill-down de 2 niveles.

    Args:
        df: DataFrame con datos de balance
        fecha: Fecha para filtrar
        tipo: 'activos' o 'pasivos' para determinar las cuentas a incluir
    """
    df_fecha = df[(df['fecha'] == fecha)]

    registros = []

    if tipo == 'activos':
        # Jerarquia de Activos:
        # Nivel 1: Bancos (codigo = '1')
        # Nivel 2: Cuentas de 2 digitos (11, 13, 14, etc.)

        # Mapeo de nombres para cuentas de activos
        cuentas_nivel2 = {
            '11': 'Fondos Disponibles',
            '13': 'Inversiones',
            '14': 'Cartera de Creditos',
            '16': 'Cuentas por Cobrar',
            '17': 'Bienes Realizables',
            '18': 'Propiedades y Equipo',
            '19': 'Otros Activos'
        }

        # NIVEL 1: Totales por banco (activos totales, codigo '1')
        activos_totales = df_fecha[df_fecha['codigo'] == '1']
        for _, row in activos_totales.iterrows():
            if pd.notna(row['valor']) and row['valor'] > 0:
                registros.append({
                    'labels': row['banco'],
                    'parents': '',
                    'values': row['valor'] / 1000,
                    'tipo': 'banco',
                    'id': row['banco']
                })

        # NIVEL 2: Cuentas de 2 digitos por banco
        for codigo, nombre in cuentas_nivel2.items():
            df_cuenta = df_fecha[df_fecha['codigo'] == codigo]
            for _, row in df_cuenta.iterrows():
                if pd.notna(row['valor']) and row['valor'] > 0:
                    id_unico = f"{row['banco']}_{nombre}"
                    registros.append({
                        'labels': nombre,
                        'parents': row['banco'],
                        'values': row['valor'] / 1000,
                        'tipo': 'cuenta_nivel2',
                        'id': id_unico
                    })

    elif tipo == 'pasivos':
        # Jerarquia de Pasivos + Patrimonio:
        # Nivel 1: Bancos (codigo = '2' + '3')
        # Nivel 2: Cuentas de 2 digitos (21, 25, 26, etc.)

        # Mapeo de nombres para cuentas de pasivos
        cuentas_nivel2 = {
            '21': 'Obligaciones con el Publico',
            '25': 'Cuentas por Pagar',
            '26': 'Obligaciones Financieras',
            '27': 'Valores en Circulacion',
            '29': 'Otros Pasivos',
            '3': 'Patrimonio'
        }

        # NIVEL 1: Totales por banco (pasivo total + patrimonio)
        # Obtener codigo '2' (pasivo total) y '3' (patrimonio)
        for _, row_banco in df_fecha[df_fecha['codigo'] == '1'].iterrows():
            banco = row_banco['banco']

            # Sumar pasivo total (codigo '2') + patrimonio (codigo '3')
            valor_pasivo = df_fecha[(df_fecha['banco'] == banco) & (df_fecha['codigo'] == '2')]['valor'].sum()
            valor_patrimonio = df_fecha[(df_fecha['banco'] == banco) & (df_fecha['codigo'] == '3')]['valor'].sum()
            valor_total = valor_pasivo + valor_patrimonio

            if valor_total > 0:
                registros.append({
                    'labels': banco,
                    'parents': '',
                    'values': valor_total / 1000,
                    'tipo': 'banco',
                    'id': banco
                })

        # NIVEL 2: Cuentas de 2 digitos por banco
        for codigo, nombre in cuentas_nivel2.items():
            df_cuenta = df_fecha[df_fecha['codigo'] == codigo]
            for _, row in df_cuenta.iterrows():
                if pd.notna(row['valor']) and row['valor'] > 0:
                    id_unico = f"{row['banco']}_{nombre}"
                    registros.append({
                        'labels': nombre,
                        'parents': row['banco'],
                        'values': row['valor'] / 1000,
                        'tipo': 'cuenta_nivel2',
                        'id': id_unico
                    })

    df_tree = pd.DataFrame(registros)

    # Calcular participaciones solo para el nivel raiz
    if not df_tree.empty:
        total_sistema = df_tree[df_tree['parents'] == '']['values'].sum()
        if total_sistema > 0:
            df_tree['participacion'] = (df_tree['values'] / total_sistema) * 100
        else:
            df_tree['participacion'] = 0

    return df_tree


# =============================================================================
# PAGINA PRINCIPAL
# =============================================================================

def main():
    st.title("📊 Panorama del Sistema Bancario")
    st.markdown("Visión general del sistema financiero ecuatoriano.")

    # Cargar datos
    try:
        df_balance, calidad = cargar_balance()
    except Exception as e:
        st.error(f"Error al cargar datos: {e}")
        return

    # Sidebar - Filtros
    st.sidebar.markdown("### Configuración")

    fechas = obtener_fechas_disponibles(df_balance)
    fecha_seleccionada = st.sidebar.selectbox(
        "Fecha de análisis",
        options=fechas,
        format_func=lambda x: x.strftime('%B %Y').title(),
        index=0
    )

    # Obtener fecha anterior (12 meses atras)
    idx_fecha = list(fechas).index(fecha_seleccionada)
    fecha_anterior = fechas[idx_fecha + 12] if idx_fecha + 12 < len(fechas) else None

    # ==========================================================================
    # SECCION 1: KPIs PRINCIPALES
    # ==========================================================================

    st.markdown("### Indicadores del Sistema")

    metricas = calcular_metricas_sistema(df_balance, fecha_seleccionada)

    # Calcular deltas si hay fecha anterior
    deltas = {}
    if fecha_anterior:
        metricas_ant = calcular_metricas_sistema(df_balance, fecha_anterior)
        for key in ['total_activos', 'total_cartera', 'total_depositos', 'total_patrimonio']:
            if metricas_ant.get(key, 0) > 0:
                deltas[key] = ((metricas[key] - metricas_ant[key]) / metricas_ant[key]) * 100

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        delta = deltas.get('total_activos')
        render_kpi_card(
            f"${metricas['total_activos']:,.0f}M",
            "Total Activos",
            delta=delta,
            delta_label="vs año ant."
        )

    with col2:
        delta = deltas.get('total_cartera')
        render_kpi_card(
            f"${metricas['total_cartera']:,.0f}M",
            "Cartera Creditos",
            delta=delta,
            delta_label="vs año ant."
        )

    with col3:
        delta = deltas.get('total_depositos')
        render_kpi_card(
            f"${metricas['total_depositos']:,.0f}M",
            "Depositos Publico",
            delta=delta,
            delta_label="vs año ant."
        )

    with col4:
        delta = deltas.get('total_patrimonio')
        render_kpi_card(
            f"${metricas['total_patrimonio']:,.0f}M",
            "Patrimonio",
            delta=delta,
            delta_label="vs año ant."
        )

    with col5:
        render_kpi_card(
            f"{metricas['num_bancos']}",
            "Bancos Activos",
            color=COLORES['acento']
        )

    st.markdown("---")

    # ==========================================================================
    # SECCION 2: MAPA DE MERCADO Y RANKING
    # ==========================================================================

    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.markdown("### Mapa de Activos por Banco")
        st.caption("Haz clic en un banco para ver la composición de sus activos")
        df_tree = obtener_datos_treemap_jerarquico(df_balance, fecha_seleccionada, tipo='activos')

        if not df_tree.empty and df_tree['values'].sum() > 0:
            fig_tree = crear_treemap(
                df_tree,
                jerarquico=True,
                altura=500
            )
            st.plotly_chart(fig_tree, use_container_width=True)
        else:
            st.warning("No hay datos de activos disponibles para esta fecha.")

    with col_right:
        st.markdown("### Ranking por Activos")
        st.caption("Todos los bancos del sistema")

        # Obtener ranking completo (todos los bancos)
        ranking = obtener_ranking_bancos(
            df_balance, fecha_seleccionada,
            CODIGOS_BALANCE['activo_total'], 50  # Suficiente para todos
        )

        if not ranking.empty:
            fig_rank = crear_ranking_barras(
                ranking,
                x_col='valor_millones',
                y_col='banco',
                formato_valor="${:,.0f}M"
            )
            # Ajustar altura segun cantidad de bancos
            fig_rank.update_layout(height=max(400, len(ranking) * 25))
            st.plotly_chart(fig_rank, use_container_width=True)

    st.markdown("---")

    # ==========================================================================
    # SECCION 2B: MAPA DE PASIVOS Y RANKING
    # ==========================================================================

    col_left2, col_right2 = st.columns([2, 1])

    with col_left2:
        st.markdown("### Mapa de Pasivos y Patrimonio por Banco")
        st.caption("Haz clic en un banco para ver la composición de sus pasivos")
        df_tree_pasivos = obtener_datos_treemap_jerarquico(df_balance, fecha_seleccionada, tipo='pasivos')

        if not df_tree_pasivos.empty and df_tree_pasivos['values'].sum() > 0:
            fig_tree_pas = crear_treemap(
                df_tree_pasivos,
                jerarquico=True,
                altura=500
            )
            st.plotly_chart(fig_tree_pas, use_container_width=True)
        else:
            st.warning("No hay datos de pasivos disponibles para esta fecha.")

    with col_right2:
        st.markdown("### Ranking por Pasivos Totales")
        st.caption("Pasivo total (sin patrimonio)")

        # Obtener ranking de pasivos totales (codigo '2')
        ranking_pasivos = obtener_ranking_bancos(
            df_balance, fecha_seleccionada,
            CODIGOS_BALANCE['pasivo_total'], 50
        )

        if not ranking_pasivos.empty:
            fig_rank_pas = crear_ranking_barras(
                ranking_pasivos,
                x_col='valor_millones',
                y_col='banco',
                formato_valor="${:,.0f}M"
            )
            # Ajustar altura segun cantidad de bancos
            fig_rank_pas.update_layout(height=max(400, len(ranking_pasivos) * 25))
            st.plotly_chart(fig_rank_pas, use_container_width=True)

    st.markdown("---")

    # ==========================================================================
    # SECCION 3: CRECIMIENTO ANUAL POR BANCO
    # ==========================================================================

    st.markdown("### Crecimiento Anual por Banco")
    st.caption(f"Variación vs mismo mes del año anterior ({fecha_seleccionada.strftime('%B %Y')})")

    col_cartera, col_depositos = st.columns(2)

    with col_cartera:
        st.markdown("**Cartera de Créditos**")

        # Obtener datos de la fecha seleccionada y del año anterior
        df_fecha_actual = df_balance[
            (df_balance['fecha'] == fecha_seleccionada) &
            (df_balance['codigo'] == CODIGOS_BALANCE['cartera_creditos'])
        ][['banco', 'valor']].copy()

        if fecha_anterior:
            df_fecha_anterior = df_balance[
                (df_balance['fecha'] == fecha_anterior) &
                (df_balance['codigo'] == CODIGOS_BALANCE['cartera_creditos'])
            ][['banco', 'valor']].copy()

            # Merge para calcular crecimiento
            df_crec_cartera = df_fecha_actual.merge(
                df_fecha_anterior,
                on='banco',
                suffixes=('_actual', '_anterior')
            )

            # Calcular crecimiento porcentual
            df_crec_cartera['crecimiento'] = (
                (df_crec_cartera['valor_actual'] - df_crec_cartera['valor_anterior']) /
                df_crec_cartera['valor_anterior'] * 100
            )

            # Ordenar de mayor a menor crecimiento
            df_crec_cartera = df_crec_cartera.sort_values('crecimiento', ascending=True)

            # Gráfico de barras horizontales
            fig_cartera = go.Figure(go.Bar(
                x=df_crec_cartera['crecimiento'],
                y=df_crec_cartera['banco'],
                orientation='h',
                marker=dict(
                    color=df_crec_cartera['crecimiento'],
                    colorscale='RdYlGn',
                    cmin=-10,
                    cmax=30,
                ),
                text=df_crec_cartera['crecimiento'].apply(lambda x: f"{x:.1f}%"),
                textposition='outside'
            ))

            fig_cartera.update_layout(
                title="Crecimiento Anual (%)",
                height=max(400, len(df_crec_cartera) * 20),
                xaxis_title="Crecimiento (%)",
                yaxis_title="",
                showlegend=False,
                margin=dict(l=10, r=10, t=40, b=10)
            )

            # Línea de referencia en 0
            fig_cartera.add_vline(x=0, line_dash="dash", line_color="gray", line_width=1)

            st.plotly_chart(fig_cartera, use_container_width=True)
        else:
            st.info("No hay datos del año anterior para comparar.")

    with col_depositos:
        st.markdown("**Depósitos del Público**")

        # Obtener datos de la fecha seleccionada y del año anterior
        df_fecha_actual = df_balance[
            (df_balance['fecha'] == fecha_seleccionada) &
            (df_balance['codigo'] == CODIGOS_BALANCE['obligaciones_publico'])
        ][['banco', 'valor']].copy()

        if fecha_anterior:
            df_fecha_anterior = df_balance[
                (df_balance['fecha'] == fecha_anterior) &
                (df_balance['codigo'] == CODIGOS_BALANCE['obligaciones_publico'])
            ][['banco', 'valor']].copy()

            # Merge para calcular crecimiento
            df_crec_depositos = df_fecha_actual.merge(
                df_fecha_anterior,
                on='banco',
                suffixes=('_actual', '_anterior')
            )

            # Calcular crecimiento porcentual
            df_crec_depositos['crecimiento'] = (
                (df_crec_depositos['valor_actual'] - df_crec_depositos['valor_anterior']) /
                df_crec_depositos['valor_anterior'] * 100
            )

            # Ordenar de mayor a menor crecimiento
            df_crec_depositos = df_crec_depositos.sort_values('crecimiento', ascending=True)

            # Gráfico de barras horizontales
            fig_depositos = go.Figure(go.Bar(
                x=df_crec_depositos['crecimiento'],
                y=df_crec_depositos['banco'],
                orientation='h',
                marker=dict(
                    color=df_crec_depositos['crecimiento'],
                    colorscale='RdYlGn',
                    cmin=-10,
                    cmax=30,
                ),
                text=df_crec_depositos['crecimiento'].apply(lambda x: f"{x:.1f}%"),
                textposition='outside'
            ))

            fig_depositos.update_layout(
                title="Crecimiento Anual (%)",
                height=max(400, len(df_crec_depositos) * 20),
                xaxis_title="Crecimiento (%)",
                yaxis_title="",
                showlegend=False,
                margin=dict(l=10, r=10, t=40, b=10)
            )

            # Línea de referencia en 0
            fig_depositos.add_vline(x=0, line_dash="dash", line_color="gray", line_width=1)

            st.plotly_chart(fig_depositos, use_container_width=True)
        else:
            st.info("No hay datos del año anterior para comparar.")


if __name__ == "__main__":
    main()
