# -*- coding: utf-8 -*-
"""
Modulo 3: Perdidas y Ganancias
Analisis de resultados y rentabilidad del sistema bancario.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path
import sys
import calendar

sys.path.append(str(Path(__file__).parent.parent))

from utils.data_loader import cargar_pyg, cargar_balance, obtener_fechas_disponibles
from config.indicator_mapping import obtener_color_banco

# =============================================================================
# CONFIGURACION
# =============================================================================

st.set_page_config(
    page_title="Perdidas y Ganancias | Radar Bancario",
    page_icon="💰",
    layout="wide",
)

# Mapeo de cuentas principales de PYG
CUENTAS_PYG = {
    'MNI': 'Margen Neto de Intereses',
    'MBF': 'Margen Bruto Financiero',
    'MNF': 'Margen Neto Financiero',
    'MDI': 'Margen de Intermediación',
    'MOP': 'Margen Operacional',
    'GAI': 'Ganancia Antes de Impuestos',
    'GDE': 'Ganancia del Ejercicio',
}

# =============================================================================
# FUNCIONES DE DATOS
# =============================================================================

@st.cache_data
def obtener_orden_bancos_por_activos() -> list:
    """Obtiene lista de bancos ordenados por activos totales (mayor a menor)."""
    try:
        df_balance, _ = cargar_balance()
        fecha_max_bal = df_balance['fecha'].max()
        # Codigo '1' es activo total
        df_activos = df_balance[
            (df_balance['fecha'] == fecha_max_bal) &
            (df_balance['codigo'] == '1')
        ][['banco', 'valor']].copy()
        df_activos = df_activos.sort_values('valor', ascending=False)
        return df_activos['banco'].tolist()
    except Exception:
        return []


# =============================================================================
# PAGINA PRINCIPAL
# =============================================================================

def main():
    st.title("💰 Perdidas y Ganancias")
    st.markdown("Analisis de perdidas y ganancias del sistema bancario ecuatoriano.")

    # Cargar datos
    try:
        df_pyg, calidad = cargar_pyg()
    except Exception as e:
        st.error(f"Error al cargar datos de PYG: {e}")
        return

    # Lista de bancos y fechas
    bancos = sorted(df_pyg['banco'].unique().tolist())
    fechas = obtener_fechas_disponibles(df_pyg)

    # Filtrar solo registros con valor_12m valido
    df_pyg = df_pyg[df_pyg['valor_12m'].notna()]

    # Fechas disponibles
    fechas = obtener_fechas_disponibles(df_pyg)
    fecha_min = min(fechas)
    fecha_max = max(fechas)

    # Diccionario de meses
    MESES = {
        1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
        5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
        9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
    }

    # Bancos por defecto para seleccion (con nombres exactos como aparecen en los datos)
    BANCOS_DEFAULT = ['Pichincha', 'Pacifico', 'Guayaquil', 'Produbanco']

    # Filtrar solo los que existen en los datos
    bancos_exactos = [b for b in BANCOS_DEFAULT if b in bancos]
    if not bancos_exactos:
        bancos_exactos = bancos[:4]  # Fallback a los primeros 4

    # ==========================================================================
    # SECCION 1: EVOLUCION COMPARATIVA
    # ==========================================================================

    st.markdown("---")
    st.markdown("### 1. Evolucion Comparativa")
    st.caption("Compara la evolucion temporal de multiples bancos para un indicador de P&G")

    # -------------------------------------------------------------------------
    # FILA 1: Selector de Indicador
    # -------------------------------------------------------------------------
    st.markdown("**Seleccionar Indicador:**")

    cuenta_label = st.selectbox(
        "Indicador",
        options=[f"{k} - {v}" for k, v in CUENTAS_PYG.items()],
        index=6,  # GDE por defecto
        key="cuenta_pyg"
    )
    codigo_cuenta = cuenta_label.split(' - ')[0]

    # -------------------------------------------------------------------------
    # FILA 2: Selector de Bancos
    # -------------------------------------------------------------------------
    st.markdown("**Bancos a Comparar:**")
    bancos_seleccionados = st.multiselect(
        "Selecciona hasta 10 bancos",
        options=bancos,
        default=bancos_exactos,
        max_selections=10,
        key="bancos_evol_pyg",
        label_visibility="collapsed"
    )

    # -------------------------------------------------------------------------
    # FILA 3: Grafico (izquierda) + Filtro de tiempo (derecha)
    # -------------------------------------------------------------------------
    col_chart, col_tiempo = st.columns([4, 1])

    with col_tiempo:
        st.markdown("**Periodo**")
        mes_inicio = st.selectbox(
            "Mes desde",
            options=list(range(1, 13)),
            format_func=lambda x: MESES[x],
            index=0,
            key="mes_inicio_pyg"
        )
        ano_inicio = st.selectbox(
            "Año desde",
            options=range(fecha_min.year, fecha_max.year + 1),
            index=max(0, 2015 - fecha_min.year),  # Enero 2015 por defecto
            key="ano_inicio_pyg"
        )

        mes_fin = st.selectbox(
            "Mes hasta",
            options=list(range(1, 13)),
            format_func=lambda x: MESES[x],
            index=fecha_max.month - 1,
            key="mes_fin_pyg"
        )
        ano_fin = st.selectbox(
            "Año hasta",
            options=range(fecha_min.year, fecha_max.year + 1),
            index=fecha_max.year - fecha_min.year,
            key="ano_fin_pyg"
        )

        # Modo de visualizacion
        modo = st.radio(
            "Modo",
            options=['Absoluto', 'Indexado', 'Participacion'],
            index=0,
            key="modo_pyg"
        )

        # Incluir total del sistema
        incluir_sistema = st.checkbox(
            "Incluir Total Sistema",
            value=False,
            key="incluir_sistema_pyg"
        )

    with col_chart:
        fecha_inicio_sel = pd.Timestamp(year=ano_inicio, month=mes_inicio, day=1)
        # Usar ultimo dia del mes para coincidir con formato de datos
        last_day_fin = calendar.monthrange(ano_fin, mes_fin)[1]
        fecha_fin_sel = pd.Timestamp(year=ano_fin, month=mes_fin, day=last_day_fin)

        if bancos_seleccionados:
            fig_evol = go.Figure()

            for i, banco in enumerate(bancos_seleccionados):
                df_banco = df_pyg[
                    (df_pyg['banco'] == banco) &
                    (df_pyg['codigo'] == codigo_cuenta) &
                    (df_pyg['fecha'] >= fecha_inicio_sel) &
                    (df_pyg['fecha'] <= fecha_fin_sel)
                ].copy().sort_values('fecha')

                if not df_banco.empty:
                    df_banco['valor_millones'] = df_banco['valor_12m'] / 1000

                    if modo == 'Indexado':
                        base = df_banco['valor_millones'].iloc[0]
                        y_data = (df_banco['valor_millones'] / base * 100) if base != 0 else df_banco['valor_millones'] * 0
                        y_label = "Indice (Base 100)"
                    elif modo == 'Participacion':
                        # Calcular participacion sobre total del sistema
                        df_total = df_pyg[
                            (df_pyg['codigo'] == codigo_cuenta) &
                            (df_pyg['fecha'] >= fecha_inicio_sel) &
                            (df_pyg['fecha'] <= fecha_fin_sel)
                        ].groupby('fecha')['valor_12m'].sum().reset_index()
                        df_banco = df_banco.merge(df_total, on='fecha', suffixes=('', '_total'))
                        y_data = (df_banco['valor_12m'] / df_banco['valor_12m_total'] * 100)
                        y_label = "Participacion (%)"
                    else:  # Absoluto
                        y_data = df_banco['valor_millones']
                        y_label = "Millones USD (12M)"

                    color_banco = obtener_color_banco(banco)
                    fig_evol.add_trace(go.Scatter(
                        x=df_banco['fecha'],
                        y=y_data,
                        name=banco,
                        mode='lines',
                        line=dict(width=2, color=color_banco),
                        hovertemplate='<b>%{fullData.name}</b><br>Fecha: %{x|%b %Y}<br>Valor: %{y:,.1f}<extra></extra>'
                    ))

            # Agregar total del sistema si se solicita
            if incluir_sistema and modo == 'Absoluto':
                df_sistema = df_pyg[
                    (df_pyg['codigo'] == codigo_cuenta) &
                    (df_pyg['fecha'] >= fecha_inicio_sel) &
                    (df_pyg['fecha'] <= fecha_fin_sel)
                ].groupby('fecha')['valor_12m'].sum().reset_index()
                df_sistema['valor_millones'] = df_sistema['valor_12m'] / 1000

                fig_evol.add_trace(go.Scatter(
                    x=df_sistema['fecha'],
                    y=df_sistema['valor_millones'],
                    name='TOTAL SISTEMA',
                    mode='lines',
                    line=dict(width=3, dash='dash', color='black'),
                    hovertemplate='<b>%{fullData.name}</b><br>Fecha: %{x|%b %Y}<br>Valor: %{y:,.1f}M<extra></extra>'
                ))

            fig_evol.update_layout(
                title=f"Evolucion: {CUENTAS_PYG[codigo_cuenta]}",
                height=450,
                xaxis_title="Fecha",
                yaxis_title=y_label,
                hovermode="x unified",
                legend=dict(orientation="h", y=-0.2, x=0.5, xanchor="center"),
                margin=dict(l=10, r=10, t=40, b=80)
            )

            st.plotly_chart(fig_evol, use_container_width=True)
        else:
            st.info("Selecciona al menos un banco para visualizar.")

    st.markdown("---")

    # ==========================================================================
    # SECCION 2: RANKING POR BANCO
    # ==========================================================================

    st.markdown("### 2. Ranking de Bancos por Indicador")
    st.caption("Comparacion de valores de todos los bancos para un indicador y mes especificos")

    # Filtros
    col_f1, col_f2, col_f3 = st.columns(3)

    with col_f1:
        cuenta_label_rank = st.selectbox(
            "Indicador",
            options=[f"{k} - {v}" for k, v in CUENTAS_PYG.items()],
            index=6,  # GDE por defecto
            key="cuenta_rank_pyg"
        )
        codigo_rank = cuenta_label_rank.split(' - ')[0]

    with col_f2:
        mes_rank = st.selectbox(
            "Mes",
            options=list(MESES.keys()),
            format_func=lambda x: MESES[x],
            index=fecha_max.month - 1,  # Ultimo mes disponible
            key="mes_rank_pyg"
        )

    with col_f3:
        ano_rank = st.selectbox(
            "Año",
            options=range(fecha_min.year, fecha_max.year + 1),
            index=fecha_max.year - fecha_min.year,  # Ultimo año disponible
            key="ano_rank_pyg"
        )

    # Usar ultimo dia del mes para coincidir con formato de datos
    last_day_rank = calendar.monthrange(ano_rank, mes_rank)[1]
    fecha_rank = pd.Timestamp(year=ano_rank, month=mes_rank, day=last_day_rank)

    # Obtener datos de ranking
    df_rank = df_pyg[
        (df_pyg['fecha'] == fecha_rank) &
        (df_pyg['codigo'] == codigo_rank)
    ].copy()

    if not df_rank.empty:
        df_rank['valor_millones'] = df_rank['valor_12m'] / 1000
        df_rank = df_rank.sort_values('valor_millones', ascending=True)

        # Asignar colores consistentes por banco
        colores_rank = [obtener_color_banco(banco) for banco in df_rank['banco']]

        # Crear grafico de barras horizontales
        fig_rank = go.Figure(go.Bar(
            x=df_rank['valor_millones'],
            y=df_rank['banco'],
            orientation='h',
            marker=dict(
                color=colores_rank
            ),
            text=df_rank['valor_millones'].apply(lambda x: f"${x:,.0f}M"),
            textposition='outside',
            hovertemplate='<b>%{y}</b><br>Valor: $%{x:,.0f}M<extra></extra>'
        ))

        fig_rank.update_layout(
            title=f"{CUENTAS_PYG[codigo_rank]} - {MESES[mes_rank]} {ano_rank}",
            height=max(400, len(df_rank) * 25),
            xaxis_title="Millones USD (12M)",
            yaxis_title="",
            showlegend=False,
            margin=dict(l=10, r=10, t=40, b=40)
        )

        st.plotly_chart(fig_rank, use_container_width=True)

        # Estadisticas del sistema
        col_s1, col_s2, col_s3 = st.columns(3)
        with col_s1:
            total_sistema = df_rank['valor_millones'].sum()
            st.metric("Total Sistema", f"${total_sistema:,.0f}M")
        with col_s2:
            participacion_top1 = (df_rank['valor_millones'].max() / total_sistema * 100) if total_sistema > 0 else 0
            st.metric("Participacion #1", f"{participacion_top1:.1f}%")
        with col_s3:
            participacion_top5 = (df_rank.head(5)['valor_millones'].sum() / total_sistema * 100) if len(df_rank) >= 5 else 0
            st.metric("Concentracion Top 5", f"{participacion_top5:.1f}%")
    else:
        st.warning("No hay datos disponibles para el periodo seleccionado.")



if __name__ == "__main__":
    main()
