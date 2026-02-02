# -*- coding: utf-8 -*-
"""
Módulo 2: Balance General
Análisis temporal de las cuentas de balance del sistema bancario.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))

from utils.data_loader import cargar_balance, obtener_fechas_disponibles
from utils.charts import COLORES
from config.indicator_mapping import CODIGOS_BALANCE, ETIQUETAS_BALANCE, COLORES_BANCOS, obtener_color_banco

# =============================================================================
# CONFIGURACION
# =============================================================================

st.set_page_config(
    page_title="Balance General | Radar Bancario",
    page_icon="📊",
    layout="wide",
)

# Bancos preseleccionados por defecto
BANCOS_DEFAULT = ['Pichincha', 'Pacifico', 'Guayaquil', 'Produbanco']

# Nombres de meses en español
MESES = {
    1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
    5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
    9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
}

# =============================================================================
# FUNCIONES DE DATOS
# =============================================================================

@st.cache_data
def obtener_jerarquia_cuentas(df: pd.DataFrame) -> dict:
    """
    Construye un diccionario jerárquico de cuentas.
    Retorna: {codigo_1d: {nombre, subcuentas: {codigo_2d: {nombre, subcuentas: {codigo_4d: {nombre, subcuentas: {codigo_6d: nombre}}}}}}}
    """
    cuentas = df[['codigo', 'cuenta']].drop_duplicates()
    cuentas = cuentas[cuentas['codigo'].str.match(r'^[0-9]+$', na=False)]

    jerarquia = {}

    # Nivel 1: 1 dígito (activos, pasivos, patrimonio, contingentes, orden)
    for _, row in cuentas[cuentas['codigo'].str.len() == 1].iterrows():
        if row['codigo'] in ['1', '2', '3', '6', '7']:  # Incluir cuentas de orden
            jerarquia[row['codigo']] = {
                'nombre': row['cuenta'],
                'subcuentas': {}
            }

    # Nivel 2: 2 dígitos
    for _, row in cuentas[cuentas['codigo'].str.len() == 2].iterrows():
        parent = row['codigo'][0]
        if parent in jerarquia:
            jerarquia[parent]['subcuentas'][row['codigo']] = {
                'nombre': row['cuenta'],
                'subcuentas': {}
            }

    # Nivel 3: 4 dígitos
    for _, row in cuentas[cuentas['codigo'].str.len() == 4].iterrows():
        parent_1d = row['codigo'][0]
        parent_2d = row['codigo'][:2]
        if parent_1d in jerarquia and parent_2d in jerarquia[parent_1d]['subcuentas']:
            jerarquia[parent_1d]['subcuentas'][parent_2d]['subcuentas'][row['codigo']] = {
                'nombre': row['cuenta'],
                'subcuentas': {}
            }

    # Nivel 4: 6 dígitos
    for _, row in cuentas[cuentas['codigo'].str.len() == 6].iterrows():
        parent_1d = row['codigo'][0]
        parent_2d = row['codigo'][:2]
        parent_4d = row['codigo'][:4]
        if (parent_1d in jerarquia and
            parent_2d in jerarquia[parent_1d]['subcuentas'] and
            parent_4d in jerarquia[parent_1d]['subcuentas'][parent_2d]['subcuentas']):
            jerarquia[parent_1d]['subcuentas'][parent_2d]['subcuentas'][parent_4d]['subcuentas'][row['codigo']] = row['cuenta']

    return jerarquia


@st.cache_data
def obtener_serie_banco(df: pd.DataFrame, banco: str, codigo: str) -> pd.DataFrame:
    """Obtiene serie temporal de un banco para una cuenta especifica."""
    df_filtrado = df[(df['banco'] == banco) & (df['codigo'] == codigo)].copy()
    df_filtrado = df_filtrado.sort_values('fecha')
    df_filtrado['valor_millones'] = df_filtrado['valor'] / 1000
    return df_filtrado[['fecha', 'valor', 'valor_millones']]


@st.cache_data
def obtener_serie_sistema(df: pd.DataFrame, codigo: str) -> pd.DataFrame:
    """Obtiene serie temporal agregada del sistema."""
    df_filtrado = df[df['codigo'] == codigo].copy()
    serie = df_filtrado.groupby('fecha')['valor'].sum().reset_index()
    serie['valor_millones'] = serie['valor'] / 1000
    serie = serie.sort_values('fecha')
    return serie


@st.cache_data
def obtener_datos_heatmap_mensual(df_completo: pd.DataFrame, codigo: str, bancos: list = None,
                                   fecha_inicio: pd.Timestamp = None, fecha_fin: pd.Timestamp = None) -> pd.DataFrame:
    """Prepara datos para heatmap de crecimiento YoY mensual por banco.

    Calcula el crecimiento de cada mes vs el mismo mes del año anterior.
    Retorna matriz: filas = bancos, columnas = fechas (YYYY-MM)

    NOTA: Usa df_completo (sin filtrar) para calcular YoY correctamente,
    luego filtra el resultado por fecha_inicio/fecha_fin.
    """
    df_filtrado = df_completo[df_completo['codigo'] == codigo].copy()

    if bancos:
        df_filtrado = df_filtrado[df_filtrado['banco'].isin(bancos)]

    if df_filtrado.empty:
        return pd.DataFrame()

    df_filtrado['año'] = df_filtrado['fecha'].dt.year
    df_filtrado['mes'] = df_filtrado['fecha'].dt.month
    df_filtrado['valor_millones'] = df_filtrado['valor'] / 1000

    # Crear columna fecha_str para el pivote
    df_filtrado['fecha_str'] = df_filtrado['fecha'].dt.strftime('%Y-%m')

    # Calcular crecimiento YoY: cada mes vs mismo mes año anterior
    df_filtrado = df_filtrado.sort_values(['banco', 'año', 'mes'])

    # Para cada banco y mes, calcular variación vs año anterior
    df_filtrado['valor_ano_anterior'] = df_filtrado.groupby(['banco', 'mes'])['valor_millones'].shift(1)
    df_filtrado['crecimiento_yoy'] = ((df_filtrado['valor_millones'] / df_filtrado['valor_ano_anterior']) - 1) * 100

    # Filtrar por rango de fechas si se especifica
    if fecha_inicio is not None:
        df_filtrado = df_filtrado[df_filtrado['fecha'] >= fecha_inicio]
    if fecha_fin is not None:
        df_filtrado = df_filtrado[df_filtrado['fecha'] <= fecha_fin]

    if df_filtrado.empty:
        return pd.DataFrame()

    # Pivotar: filas = bancos, columnas = fecha_str
    heatmap_data = df_filtrado.pivot_table(
        index='banco',
        columns='fecha_str',
        values='crecimiento_yoy',
        aggfunc='first'
    )

    # Ordenar bancos por valor del último período disponible (más grande arriba)
    ultima_fecha = df_filtrado['fecha'].max()
    valores_ultima_fecha = df_filtrado[df_filtrado['fecha'] == ultima_fecha].set_index('banco')['valor_millones']
    orden_bancos = valores_ultima_fecha.sort_values(ascending=True).index
    heatmap_data = heatmap_data.reindex(orden_bancos)

    return heatmap_data


@st.cache_data
def obtener_valores_bancos_mes(df: pd.DataFrame, codigo: str, fecha: pd.Timestamp) -> pd.DataFrame:
    """Obtiene valores de todos los bancos para una cuenta y mes especificos.

    Args:
        df: DataFrame de balance
        codigo: Codigo de cuenta contable
        fecha: Fecha especifica (se usara año y mes)

    Returns:
        DataFrame con columnas: banco, valor_millones (ordenado descendente)
    """
    # Filtrar por codigo y fecha (año y mes)
    df_filtrado = df[
        (df['codigo'] == codigo) &
        (df['fecha'].dt.year == fecha.year) &
        (df['fecha'].dt.month == fecha.month)
    ].copy()

    if df_filtrado.empty:
        return pd.DataFrame()

    # Calcular valor en millones
    df_filtrado['valor_millones'] = df_filtrado['valor'] / 1000

    # Filtrar solo valores positivos y que no sean NaN
    df_filtrado = df_filtrado[
        (df_filtrado['valor_millones'].notna()) &
        (df_filtrado['valor_millones'] > 0)
    ]

    if df_filtrado.empty:
        return pd.DataFrame()

    # Agrupar por banco (en caso de duplicados, tomar el primer valor)
    resultado = df_filtrado.groupby('banco', as_index=False).agg({
        'valor_millones': 'first'
    })

    # Ordenar por valor descendente
    resultado = resultado.sort_values('valor_millones', ascending=False)

    return resultado


# =============================================================================
# PAGINA PRINCIPAL
# =============================================================================

def main():
    st.title("📊 Balance General")
    st.markdown("Análisis temporal avanzado del sistema bancario ecuatoriano.")

    # CSS para ampliar el ancho de los selectbox
    st.markdown("""
        <style>
        div[data-baseweb="select"] > div {
            max-width: none !important;
        }
        div[data-baseweb="select"] span {
            white-space: normal !important;
            overflow: visible !important;
            text-overflow: clip !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # Cargar datos
    try:
        df_balance, calidad = cargar_balance()
    except Exception as e:
        st.error(f"Error al cargar datos: {e}")
        return

    # Lista de bancos
    bancos = sorted(df_balance['banco'].unique().tolist())
    fechas = obtener_fechas_disponibles(df_balance)

    # ==========================================================================
    # SIDEBAR - INFORMACION GENERAL
    # ==========================================================================

    # Rango de fechas disponibles
    fecha_min = df_balance['fecha'].min()
    fecha_max = df_balance['fecha'].max()

    st.sidebar.markdown("### Información del Módulo")
    st.sidebar.markdown(f"**Datos disponibles:** {fecha_min.strftime('%b %Y')} - {fecha_max.strftime('%b %Y')}")
    st.sidebar.markdown(f"**Bancos:** {len(bancos)}")
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Nota:** Los filtros de tiempo y cuenta estan disponibles en cada seccion.")

    # ==========================================================================
    # SECCION 1: EVOLUCION COMPARATIVA
    # ==========================================================================

    st.markdown("---")
    st.markdown("### 1. Evolución Comparativa")
    st.caption("Compara la evolución temporal de múltiples bancos")

    # Obtener jerarquia de cuentas
    jerarquia = obtener_jerarquia_cuentas(df_balance)

    # -------------------------------------------------------------------------
    # FILA 1: Filtros de Cuenta (ARRIBA del gráfico)
    # -------------------------------------------------------------------------
    st.markdown("**Seleccionar Cuenta:**")

    # Construir opciones de cuenta nivel 1
    opciones_nivel1 = {f"{k} - {v['nombre']}": k for k, v in jerarquia.items()}

    col_n1, col_n2, col_n3, col_n4 = st.columns(4)

    with col_n1:
        nivel1_label = st.selectbox(
            "Categoria",
            options=list(opciones_nivel1.keys()),
            index=0,
            key="cuenta_nivel1"
        )
        codigo_nivel1 = opciones_nivel1[nivel1_label]

    # Nivel 2: Subcuenta
    subcuentas_nivel2 = jerarquia[codigo_nivel1]['subcuentas']
    opciones_nivel2 = {"Todas (agregado)": codigo_nivel1}
    for k, v in subcuentas_nivel2.items():
        # Mostrar nombre completo sin truncar
        label = f"{k} - {v['nombre']}"
        opciones_nivel2[label] = k

    with col_n2:
        nivel2_label = st.selectbox(
            "Grupo",
            options=list(opciones_nivel2.keys()),
            index=0,
            key="cuenta_nivel2"
        )
        codigo_nivel2 = opciones_nivel2[nivel2_label]

    # Nivel 3: Cuenta de 4 dígitos
    codigo_cuenta_final = codigo_nivel2

    with col_n3:
        if codigo_nivel2 != codigo_nivel1 and codigo_nivel2 in subcuentas_nivel2:
            subcuentas_nivel3 = subcuentas_nivel2[codigo_nivel2]['subcuentas']
            if subcuentas_nivel3:
                opciones_nivel3 = {"Todas (agregado)": codigo_nivel2}
                for k, v in subcuentas_nivel3.items():
                    # Mostrar nombre completo sin truncar
                    if isinstance(v, dict):
                        label = f"{k} - {v['nombre']}"
                    else:
                        label = f"{k} - {str(v)}"
                    opciones_nivel3[label] = k

                nivel3_label = st.selectbox(
                    "Subcuenta",
                    options=list(opciones_nivel3.keys()),
                    index=0,
                    key="cuenta_nivel3"
                )
                codigo_nivel3 = opciones_nivel3[nivel3_label]
                codigo_cuenta_final = codigo_nivel3
            else:
                codigo_nivel3 = codigo_nivel2
                st.selectbox("Subcuenta", options=["N/A"], disabled=True, key="cuenta_nivel3_disabled")
        else:
            codigo_nivel3 = codigo_nivel2
            st.selectbox("Subcuenta", options=["N/A"], disabled=True, key="cuenta_nivel3_disabled2")

    # Nivel 4: Cuenta de 6 dígitos
    with col_n4:
        if (codigo_nivel3 != codigo_nivel2 and
            codigo_nivel2 != codigo_nivel1 and
            codigo_nivel2 in subcuentas_nivel2 and
            codigo_nivel3 in subcuentas_nivel2[codigo_nivel2]['subcuentas'] and
            isinstance(subcuentas_nivel2[codigo_nivel2]['subcuentas'][codigo_nivel3], dict)):
            subcuentas_nivel4 = subcuentas_nivel2[codigo_nivel2]['subcuentas'][codigo_nivel3]['subcuentas']
            if subcuentas_nivel4:
                opciones_nivel4 = {"Todas (agregado)": codigo_nivel3}
                for k, v in subcuentas_nivel4.items():
                    label = f"{k} - {str(v)}"
                    opciones_nivel4[label] = k

                nivel4_label = st.selectbox(
                    "Detalle",
                    options=list(opciones_nivel4.keys()),
                    index=0,
                    key="cuenta_nivel4"
                )
                codigo_cuenta_final = opciones_nivel4[nivel4_label]
            else:
                st.selectbox("Detalle", options=["N/A"], disabled=True, key="cuenta_nivel4_disabled")
        else:
            st.selectbox("Detalle", options=["N/A"], disabled=True, key="cuenta_nivel4_disabled2")

    # -------------------------------------------------------------------------
    # FILA 2: Selector de Bancos
    # -------------------------------------------------------------------------
    st.markdown("**Bancos a Comparar:**")
    bancos_default_disponibles = [b for b in BANCOS_DEFAULT if b in bancos]
    bancos_seleccionados = st.multiselect(
        "Selecciona hasta 10 bancos",
        options=bancos,
        default=bancos_default_disponibles,
        max_selections=10,
        key="bancos_evol",
        label_visibility="collapsed"
    )

    # -------------------------------------------------------------------------
    # FILA 3: Gráfico (izquierda) + Filtro de tiempo (derecha)
    # -------------------------------------------------------------------------
    col_chart, col_tiempo = st.columns([4, 1])

    with col_tiempo:
        st.markdown("**Periodo**")
        mes_inicio = st.selectbox(
            "Mes desde",
            options=list(range(1, 13)),
            format_func=lambda x: MESES[x],
            index=0,
            key="mes_inicio_evol"
        )
        ano_inicio_evol = st.selectbox(
            "Año desde",
            options=range(fecha_min.year, fecha_max.year + 1),
            index=max(0, 2015 - fecha_min.year),
            key="ano_inicio_evol"
        )
        st.markdown("---")
        mes_fin = st.selectbox(
            "Mes hasta",
            options=list(range(1, 13)),
            format_func=lambda x: MESES[x],
            index=11,
            key="mes_fin_evol"
        )
        ano_fin_evol = st.selectbox(
            "Año hasta",
            options=range(fecha_min.year, fecha_max.year + 1),
            index=fecha_max.year - fecha_min.year,
            key="ano_fin_evol"
        )

        st.markdown("---")

        modo_viz = st.radio(
            "Modo",
            options=["Valores Absolutos", "Indexado (Base 100)", "Participacion %"],
            index=0,
            key="modo_evol"
        )
        incluir_sistema = st.checkbox("Incluir Total Sistema", value=False, key="sistema_evol")

    # Crear fechas de filtro
    fecha_inicio_evol = pd.Timestamp(f"{ano_inicio_evol}-{mes_inicio:02d}-01")
    if mes_fin == 12:
        fecha_fin_evol = pd.Timestamp(f"{ano_fin_evol}-12-31")
    else:
        fecha_fin_evol = pd.Timestamp(f"{ano_fin_evol}-{mes_fin + 1:02d}-01") - pd.Timedelta(days=1)

    # Filtrar datos
    df_evol = df_balance[
        (df_balance['fecha'] >= fecha_inicio_evol) &
        (df_balance['fecha'] <= fecha_fin_evol)
    ]

    # Obtener nombre de la cuenta seleccionada
    cuenta_info = df_balance[df_balance['codigo'] == codigo_cuenta_final]['cuenta'].iloc[0] if \
        not df_balance[df_balance['codigo'] == codigo_cuenta_final].empty else codigo_cuenta_final

    # Dibujar gráfico
    with col_chart:
        if bancos_seleccionados:
            fig_evol = go.Figure()
            y_title = "Millones USD"

            # Serie del sistema para participacion
            if modo_viz == "Participacion %" or incluir_sistema:
                serie_sistema = obtener_serie_sistema(df_evol, codigo_cuenta_final)

            for banco in bancos_seleccionados:
                serie = obtener_serie_banco(df_evol, banco, codigo_cuenta_final)

                if not serie.empty:
                    if modo_viz == "Valores Absolutos":
                        y_values = serie['valor_millones']
                        y_title = "Millones USD"
                    elif modo_viz == "Indexado (Base 100)":
                        base = serie['valor_millones'].iloc[0]
                        y_values = (serie['valor_millones'] / base) * 100 if base > 0 else serie['valor_millones']
                        y_title = "Indice (Base 100)"
                    else:  # Participacion %
                        serie_merged = serie.merge(serie_sistema[['fecha', 'valor_millones']], on='fecha', suffixes=('', '_sistema'))
                        y_values = (serie_merged['valor_millones'] / serie_merged['valor_millones_sistema']) * 100
                        serie = serie_merged
                        y_title = "Participacion (%)"

                    color_banco = obtener_color_banco(banco)
                    fig_evol.add_trace(go.Scatter(
                        x=serie['fecha'],
                        y=y_values,
                        name=banco,
                        mode='lines',
                        line=dict(width=2, color=color_banco),
                        hovertemplate=f'<b>{banco}</b><br>Fecha: %{{x|%b %Y}}<br>Valor: %{{y:,.1f}}<extra></extra>'
                    ))

            # Agregar sistema si se solicita
            if incluir_sistema and modo_viz != "Participacion %":
                serie_sis = obtener_serie_sistema(df_evol, codigo_cuenta_final)
                if modo_viz == "Indexado (Base 100)":
                    base = serie_sis['valor_millones'].iloc[0]
                    y_values = (serie_sis['valor_millones'] / base) * 100 if base > 0 else serie_sis['valor_millones']
                else:
                    y_values = serie_sis['valor_millones']

                fig_evol.add_trace(go.Scatter(
                    x=serie_sis['fecha'],
                    y=y_values,
                    name="SISTEMA",
                    mode='lines',
                    line=dict(width=3, color='black', dash='dash'),
                ))

            titulo_cuenta = cuenta_info if len(str(cuenta_info)) < 50 else str(cuenta_info)[:47] + "..."

            fig_evol.update_layout(
                title=f"Evolución: {titulo_cuenta}",
                height=450,
                xaxis_title="Fecha",
                yaxis_title=y_title,
                hovermode="x unified",
                legend=dict(orientation="h", y=-0.15, x=0.5, xanchor="center"),
                margin=dict(l=10, r=10, t=40, b=80)
            )

            st.plotly_chart(fig_evol, use_container_width=True)
        else:
            st.info("Selecciona al menos un banco para visualizar.")

    # ==========================================================================
    # SECCION 2: HEATMAP TEMPORAL
    # ==========================================================================

    st.markdown("---")
    st.markdown("### 2. Heatmap de Variacion Porcentual Anual")
    st.caption("Matriz Banco x Mes mostrando crecimiento YoY (cada mes vs mismo mes del año anterior)")

    # -------------------------------------------------------------------------
    # FILA 1: Filtros de Cuenta (ARRIBA del gráfico)
    # -------------------------------------------------------------------------
    # Construir opciones de cuenta nivel 1
    opciones_nivel1_h = {f"{k} - {v['nombre']}": k for k, v in jerarquia.items()}

    col_n1_h, col_n2_h, col_n3_h, col_n4_h = st.columns(4)

    with col_n1_h:
        nivel1_label_h = st.selectbox(
            "Categoria",
            options=list(opciones_nivel1_h.keys()),
            index=0,
            key="cuenta_nivel1_heat"
        )
        codigo_nivel1_h = opciones_nivel1_h[nivel1_label_h]

    # Nivel 2: Subcuenta
    subcuentas_nivel2_h = jerarquia[codigo_nivel1_h]['subcuentas']
    opciones_nivel2_h = {"Todas (agregado)": codigo_nivel1_h}
    for k, v in subcuentas_nivel2_h.items():
        # Mostrar nombre completo sin truncar
        label = f"{k} - {v['nombre']}"
        opciones_nivel2_h[label] = k

    with col_n2_h:
        nivel2_label_h = st.selectbox(
            "Grupo",
            options=list(opciones_nivel2_h.keys()),
            index=0,
            key="cuenta_nivel2_heat"
        )
        codigo_nivel2_h = opciones_nivel2_h[nivel2_label_h]

    # Nivel 3: Cuenta de 4 dígitos
    codigo_cuenta_heat = codigo_nivel2_h

    with col_n3_h:
        if codigo_nivel2_h != codigo_nivel1_h and codigo_nivel2_h in subcuentas_nivel2_h:
            subcuentas_nivel3_h = subcuentas_nivel2_h[codigo_nivel2_h]['subcuentas']
            if subcuentas_nivel3_h:
                opciones_nivel3_h = {"Todas (agregado)": codigo_nivel2_h}
                for k, v in subcuentas_nivel3_h.items():
                    # Mostrar nombre completo sin truncar
                    if isinstance(v, dict):
                        label = f"{k} - {v['nombre']}"
                    else:
                        label = f"{k} - {str(v)}"
                    opciones_nivel3_h[label] = k

                nivel3_label_h = st.selectbox(
                    "Subcuenta",
                    options=list(opciones_nivel3_h.keys()),
                    index=0,
                    key="cuenta_nivel3_heat"
                )
                codigo_nivel3_h = opciones_nivel3_h[nivel3_label_h]
                codigo_cuenta_heat = codigo_nivel3_h
            else:
                codigo_nivel3_h = codigo_nivel2_h
                st.selectbox("Subcuenta", options=["N/A"], disabled=True, key="cuenta_nivel3_heat_disabled")
        else:
            codigo_nivel3_h = codigo_nivel2_h
            st.selectbox("Subcuenta", options=["N/A"], disabled=True, key="cuenta_nivel3_heat_disabled2")

    # Nivel 4: Cuenta de 6 dígitos
    with col_n4_h:
        if (codigo_nivel3_h != codigo_nivel2_h and
            codigo_nivel2_h != codigo_nivel1_h and
            codigo_nivel2_h in subcuentas_nivel2_h and
            codigo_nivel3_h in subcuentas_nivel2_h[codigo_nivel2_h]['subcuentas'] and
            isinstance(subcuentas_nivel2_h[codigo_nivel2_h]['subcuentas'][codigo_nivel3_h], dict)):
            subcuentas_nivel4_h = subcuentas_nivel2_h[codigo_nivel2_h]['subcuentas'][codigo_nivel3_h]['subcuentas']
            if subcuentas_nivel4_h:
                opciones_nivel4_h = {"Todas (agregado)": codigo_nivel3_h}
                for k, v in subcuentas_nivel4_h.items():
                    label = f"{k} - {str(v)}"
                    opciones_nivel4_h[label] = k

                nivel4_label_h = st.selectbox(
                    "Detalle",
                    options=list(opciones_nivel4_h.keys()),
                    index=0,
                    key="cuenta_nivel4_heat"
                )
                codigo_cuenta_heat = opciones_nivel4_h[nivel4_label_h]
            else:
                st.selectbox("Detalle", options=["N/A"], disabled=True, key="cuenta_nivel4_heat_disabled")
        else:
            st.selectbox("Detalle", options=["N/A"], disabled=True, key="cuenta_nivel4_heat_disabled2")

    # -------------------------------------------------------------------------
    # FILA 2: Gráfico (izquierda) + Filtro de tiempo (derecha)
    # -------------------------------------------------------------------------
    col_heat_chart, col_heat_tiempo = st.columns([4, 1])

    with col_heat_tiempo:
        st.markdown("**Periodo**")
        mes_inicio_heat = st.selectbox(
            "Mes desde",
            options=list(range(1, 13)),
            format_func=lambda x: MESES[x],
            index=0,
            key="mes_inicio_heat"
        )
        ano_inicio_heat = st.selectbox(
            "Año desde",
            options=range(fecha_min.year, fecha_max.year + 1),
            index=max(0, 2015 - fecha_min.year),
            key="ano_inicio_heat"
        )
        st.markdown("---")
        mes_fin_heat = st.selectbox(
            "Mes hasta",
            options=list(range(1, 13)),
            format_func=lambda x: MESES[x],
            index=11,
            key="mes_fin_heat"
        )
        ano_fin_heat = st.selectbox(
            "Año hasta",
            options=range(fecha_min.year, fecha_max.year + 1),
            index=fecha_max.year - fecha_min.year,
            key="ano_fin_heat"
        )

    # Crear fechas de filtro
    fecha_inicio_heat = pd.Timestamp(f"{ano_inicio_heat}-{mes_inicio_heat:02d}-01")
    if mes_fin_heat == 12:
        fecha_fin_heat = pd.Timestamp(f"{ano_fin_heat}-12-31")
    else:
        fecha_fin_heat = pd.Timestamp(f"{ano_fin_heat}-{mes_fin_heat + 1:02d}-01") - pd.Timedelta(days=1)

    # Obtener nombre de la cuenta seleccionada
    cuenta_heat_info = df_balance[df_balance['codigo'] == codigo_cuenta_heat]['cuenta'].iloc[0] if \
        not df_balance[df_balance['codigo'] == codigo_cuenta_heat].empty else codigo_cuenta_heat

    # Generar datos del heatmap (usa df_balance completo para calcular YoY correctamente)
    # Sin filtro de bancos - mostrar todos
    heatmap_data = obtener_datos_heatmap_mensual(
        df_balance,  # DataFrame completo para calcular YoY
        codigo_cuenta_heat,
        None,  # Sin filtro de bancos - mostrar todos
        fecha_inicio_heat,
        fecha_fin_heat
    )

    with col_heat_chart:
        if not heatmap_data.empty:
            # Formatear etiquetas de meses para mejor lectura
            etiquetas_x = [f"{MESES[int(col.split('-')[1])][:3]} {col.split('-')[0][2:]}" for col in heatmap_data.columns]

            # Escala de colores: rojo para negativo, blanco en cero, verde para positivo
            colorscale_divergente = [
                [0.0, 'rgb(165, 0, 38)'],      # Rojo oscuro (muy negativo)
                [0.25, 'rgb(215, 48, 39)'],    # Rojo
                [0.4, 'rgb(244, 109, 67)'],    # Rojo claro
                [0.5, 'rgb(255, 255, 255)'],   # Blanco (cero)
                [0.6, 'rgb(166, 217, 106)'],   # Verde claro
                [0.75, 'rgb(102, 189, 99)'],   # Verde
                [1.0, 'rgb(0, 104, 55)'],      # Verde oscuro (muy positivo)
            ]

            fig_heat = go.Figure(data=go.Heatmap(
                z=heatmap_data.values,
                x=etiquetas_x,
                y=heatmap_data.index,
                colorscale=colorscale_divergente,
                zmid=0,
                zmin=-30,
                zmax=30,
                hovertemplate='Banco: %{y}<br>Periodo: %{x}<br>Variacion YoY: %{z:.1f}%<extra></extra>',
                colorbar=dict(title="Variacion %", ticksuffix="%")
            ))

            titulo_cuenta_h = str(cuenta_heat_info) if len(str(cuenta_heat_info)) < 50 else str(cuenta_heat_info)[:47] + "..."

            fig_heat.update_layout(
                title=f"Variacion YoY: {titulo_cuenta_h}",
                height=max(400, len(heatmap_data) * 22),
                xaxis_title="Periodo",
                yaxis_title="",
                xaxis=dict(tickangle=-45, tickfont=dict(size=9)),
                margin=dict(l=10, r=10, t=40, b=80)
            )

            st.plotly_chart(fig_heat, use_container_width=True)
        else:
            st.warning("No hay datos suficientes para el heatmap.")

    # ==========================================================================
    # SECCION 3: RANKING POR BANCO
    # ==========================================================================

    st.markdown("---")
    st.markdown("### 3. Ranking de Bancos por Cuenta")
    st.caption("Comparación de valores de todos los bancos para una cuenta y mes específicos")

    # Filtros de cuenta (usando la misma jerarquia que secciones anteriores)
    col_f1, col_f2, col_f3, col_f4 = st.columns([2, 2, 2, 2])

    with col_f1:
        # Nivel 1: Categoria
        opciones_nivel1_r = {}
        for k, v in jerarquia.items():
            # Mostrar nombre completo sin truncar
            label = f"{k} - {v['nombre']}"
            opciones_nivel1_r[label] = k

        categoria_r_label = st.selectbox(
            "Categoria",
            options=list(opciones_nivel1_r.keys()),
            index=0,
            key="categoria_r"
        )
        categoria_r = opciones_nivel1_r[categoria_r_label]

    with col_f2:
        # Nivel 2: Grupo (2 digitos)
        subcuentas_nivel2_r = jerarquia[categoria_r]['subcuentas']

        if subcuentas_nivel2_r:
            opciones_nivel2_r = {"Todas (agregado)": categoria_r}
            for k, v in subcuentas_nivel2_r.items():
                # Mostrar nombre completo sin truncar
                label = f"{k} - {v['nombre']}"
                opciones_nivel2_r[label] = k

            grupo_r_label = st.selectbox(
                "Grupo",
                options=list(opciones_nivel2_r.keys()),
                index=0,
                key="grupo_r"
            )
            grupo_r = opciones_nivel2_r[grupo_r_label]
        else:
            grupo_r = categoria_r
            st.selectbox("Grupo", options=["Sin subcuentas"], index=0, disabled=True, key="grupo_r_disabled")

    with col_f3:
        # Nivel 3: Subcuenta (4 digitos)
        if subcuentas_nivel2_r and grupo_r != categoria_r and grupo_r in subcuentas_nivel2_r:
            subcuentas_nivel3_r = subcuentas_nivel2_r[grupo_r]['subcuentas']

            if subcuentas_nivel3_r:
                opciones_nivel3_r = {"Todas (agregado)": grupo_r}
                for k, v in subcuentas_nivel3_r.items():
                    # Mostrar nombre completo sin truncar
                    if isinstance(v, dict):
                        label = f"{k} - {v['nombre']}"
                    else:
                        label = f"{k} - {str(v)}"
                    opciones_nivel3_r[label] = k

                subcuenta_r_label = st.selectbox(
                    "Subcuenta",
                    options=list(opciones_nivel3_r.keys()),
                    index=0,
                    key="subcuenta_r"
                )
                subcuenta_r = opciones_nivel3_r[subcuenta_r_label]
            else:
                subcuenta_r = grupo_r
                st.selectbox("Subcuenta", options=["Sin subcuentas"], index=0, disabled=True, key="subcuenta_r_disabled")
        else:
            subcuenta_r = grupo_r if grupo_r != categoria_r else categoria_r
            st.selectbox("Subcuenta", options=["Sin subcuentas"], index=0, disabled=True, key="subcuenta_r_disabled2")

    with col_f4:
        # Nivel 4: Detalle (6 digitos)
        if (subcuenta_r != grupo_r and
            grupo_r != categoria_r and
            subcuentas_nivel2_r and grupo_r in subcuentas_nivel2_r and
            subcuenta_r in subcuentas_nivel2_r[grupo_r]['subcuentas'] and
            isinstance(subcuentas_nivel2_r[grupo_r]['subcuentas'][subcuenta_r], dict)):
            subcuentas_nivel4_r = subcuentas_nivel2_r[grupo_r]['subcuentas'][subcuenta_r]['subcuentas']

            if subcuentas_nivel4_r:
                opciones_nivel4_r = {"Todas (agregado)": subcuenta_r}
                for k, v in subcuentas_nivel4_r.items():
                    label = f"{k} - {str(v)}"
                    opciones_nivel4_r[label] = k

                detalle_r_label = st.selectbox(
                    "Detalle",
                    options=list(opciones_nivel4_r.keys()),
                    index=0,
                    key="detalle_r"
                )
                detalle_r = opciones_nivel4_r[detalle_r_label]
            else:
                detalle_r = subcuenta_r
                st.selectbox("Detalle", options=["Sin subcuentas"], index=0, disabled=True, key="detalle_r_disabled")
        else:
            detalle_r = subcuenta_r
            st.selectbox("Detalle", options=["Sin subcuentas"], index=0, disabled=True, key="detalle_r_disabled2")

    # Determinar codigo final seleccionado
    if (subcuentas_nivel2_r and grupo_r in subcuentas_nivel2_r and
        subcuenta_r in subcuentas_nivel2_r[grupo_r]['subcuentas'] and
        isinstance(subcuentas_nivel2_r[grupo_r]['subcuentas'][subcuenta_r], dict) and
        subcuentas_nivel2_r[grupo_r]['subcuentas'][subcuenta_r]['subcuentas']):
        codigo_r = detalle_r
    elif subcuentas_nivel2_r and grupo_r in subcuentas_nivel2_r and subcuentas_nivel2_r[grupo_r]['subcuentas']:
        codigo_r = subcuenta_r
    elif subcuentas_nivel2_r:
        codigo_r = grupo_r
    else:
        codigo_r = categoria_r

    # Selector de mes y año
    col_f5, col_f6 = st.columns(2)
    with col_f5:
        mes_r = st.selectbox(
            "Mes",
            options=list(MESES.keys()),
            format_func=lambda x: MESES[x],
            index=fecha_max.month - 1,
            key="mes_r"
        )
    with col_f6:
        ano_r = st.selectbox(
            "Año",
            options=range(fecha_min.year, fecha_max.year + 1),
            index=fecha_max.year - fecha_min.year,
            key="ano_r"
        )

    # Construir fecha seleccionada
    fecha_r = pd.Timestamp(year=ano_r, month=mes_r, day=1)

    # Obtener titulo de la cuenta seleccionada
    cuenta_info = df_balance[df_balance['codigo'] == codigo_r]['cuenta'].iloc[0] if len(df_balance[df_balance['codigo'] == codigo_r]) > 0 else codigo_r
    titulo_cuenta_r = f"{codigo_r} - {cuenta_info}" if cuenta_info != codigo_r else codigo_r

    # Obtener datos de ranking
    datos_ranking = obtener_valores_bancos_mes(df_balance, codigo_r, fecha_r)

    if not datos_ranking.empty:
        # Crear grafico de barras
        fig_ranking = go.Figure()

        # Agregar barras con colores por banco
        colores = [obtener_color_banco(banco) for banco in datos_ranking['banco']]

        fig_ranking.add_trace(go.Bar(
            y=datos_ranking['banco'],
            x=datos_ranking['valor_millones'],
            orientation='h',
            marker=dict(color=colores),
            text=datos_ranking['valor_millones'].apply(lambda x: f"${x:,.0f}M"),
            textposition='outside',
            hovertemplate='Banco: %{y}<br>Valor: $%{x:,.0f}M<extra></extra>'
        ))

        altura = max(400, len(datos_ranking) * 25)

        fig_ranking.update_layout(
            title=f"Ranking: {titulo_cuenta_r} ({MESES[mes_r]} {ano_r})",
            height=altura,
            xaxis_title="Valor (Millones USD)",
            yaxis_title="",
            showlegend=False,
            margin=dict(l=10, r=10, t=40, b=10),
            yaxis=dict(autorange="reversed")  # Mayor valor arriba
        )

        st.plotly_chart(fig_ranking, use_container_width=True)

        # Estadisticas
        col_s1, col_s2, col_s3 = st.columns(3)
        with col_s1:
            st.metric("Total Sistema", f"${datos_ranking['valor_millones'].sum():,.0f}M")
        with col_s2:
            participacion_top = (datos_ranking.iloc[0]['valor_millones'] / datos_ranking['valor_millones'].sum() * 100) if len(datos_ranking) > 0 else 0
            st.metric("Participacion #1", f"{participacion_top:.1f}%")
        with col_s3:
            participacion_top5 = (datos_ranking.head(5)['valor_millones'].sum() / datos_ranking['valor_millones'].sum() * 100) if len(datos_ranking) >= 5 else 0
            st.metric("Concentracion Top 5", f"{participacion_top5:.1f}%")
    else:
        st.warning("No hay datos disponibles para el periodo seleccionado.")


if __name__ == "__main__":
    main()
