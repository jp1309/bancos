# -*- coding: utf-8 -*-
"""
Modulo 4: Indicadores CAMEL
Analisis de indicadores financieros del sistema bancario ecuatoriano.
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

from utils.data_loader import cargar_camel, cargar_balance, obtener_fechas_disponibles
from config.indicator_mapping import (
    COLORES_BANCOS,
    obtener_color_banco,
    GRUPOS_INDICADORES,
    ETIQUETAS_INDICADORES
)

# =============================================================================
# CONFIGURACION
# =============================================================================

st.set_page_config(
    page_title="CAMEL | Radar Bancario",
    page_icon="📈",
    layout="wide",
)

# Indicadores principales por categoria (usando el mapeo actualizado)
INDICADORES_PRINCIPALES = {
    'C - Capital y Solvencia': [
        ('SOL', ETIQUETAS_INDICADORES.get('SOL', 'Solvencia')),
    ],
    'A - Morosidad por Cartera': [
        ('MOR_TOT', ETIQUETAS_INDICADORES.get('MOR_TOT', 'Morosidad Total')),
        ('MOR_CONS', ETIQUETAS_INDICADORES.get('MOR_CONS', 'Morosidad Consumo')),
        ('MOR_INMOB', ETIQUETAS_INDICADORES.get('MOR_INMOB', 'Morosidad Inmobiliaria')),
        ('MOR_INMOB_VIP', ETIQUETAS_INDICADORES.get('MOR_INMOB_VIP', 'Morosidad Vivienda VIP')),
        ('MOR_VIS', ETIQUETAS_INDICADORES.get('MOR_VIS', 'Morosidad Vivienda Social')),
        ('MOR_MICRO', ETIQUETAS_INDICADORES.get('MOR_MICRO', 'Morosidad Microcredito')),
        ('MOR_EDU', ETIQUETAS_INDICADORES.get('MOR_EDU', 'Morosidad Educativo')),
        ('MOR_PROD', ETIQUETAS_INDICADORES.get('MOR_PROD', 'Morosidad Productivo')),
        ('MOR_INV_PUB', ETIQUETAS_INDICADORES.get('MOR_INV_PUB', 'Morosidad Inversion Publica')),
    ],
    'A - Cobertura por Cartera': [
        ('COB_TOT', ETIQUETAS_INDICADORES.get('COB_TOT', 'Cobertura Total')),
        ('COB_CONS', ETIQUETAS_INDICADORES.get('COB_CONS', 'Cobertura Consumo')),
        ('COB_INMOB', ETIQUETAS_INDICADORES.get('COB_INMOB', 'Cobertura Inmobiliaria')),
        ('COB_INMOB_VIP', ETIQUETAS_INDICADORES.get('COB_INMOB_VIP', 'Cobertura Vivienda VIP')),
        ('COB_VIS', ETIQUETAS_INDICADORES.get('COB_VIS', 'Cobertura Vivienda Social')),
        ('COB_MICRO', ETIQUETAS_INDICADORES.get('COB_MICRO', 'Cobertura Microcredito')),
        ('COB_EDU', ETIQUETAS_INDICADORES.get('COB_EDU', 'Cobertura Educativo')),
        ('COB_PROD', ETIQUETAS_INDICADORES.get('COB_PROD', 'Cobertura Productivo')),
        ('COB_INV_PUB', ETIQUETAS_INDICADORES.get('COB_INV_PUB', 'Cobertura Inversion Publica')),
        ('COB_COM_PRIO', ETIQUETAS_INDICADORES.get('COB_COM_PRIO', 'Cobertura Comercial Prioritario')),
        ('COB_CONS_PRIO', ETIQUETAS_INDICADORES.get('COB_CONS_PRIO', 'Cobertura Consumo Prioritario')),
    ],
    'A - Participacion por Cartera': [
        ('PART_CONS', ETIQUETAS_INDICADORES.get('PART_CONS', 'Participacion Consumo')),
        ('PART_INMOB', ETIQUETAS_INDICADORES.get('PART_INMOB', 'Participacion Inmobiliaria')),
        ('PART_INMOB_VIP', ETIQUETAS_INDICADORES.get('PART_INMOB_VIP', 'Participacion Vivienda VIP')),
        ('PART_VIS', ETIQUETAS_INDICADORES.get('PART_VIS', 'Participacion Vivienda Social')),
        ('PART_MICRO', ETIQUETAS_INDICADORES.get('PART_MICRO', 'Participacion Microcredito')),
        ('PART_EDU', ETIQUETAS_INDICADORES.get('PART_EDU', 'Participacion Educativo')),
        ('PART_PROD', ETIQUETAS_INDICADORES.get('PART_PROD', 'Participacion Productivo')),
        ('PART_INV_PUB', ETIQUETAS_INDICADORES.get('PART_INV_PUB', 'Participacion Inversion Publica')),
    ],
    'A - Calidad de Activos': [
        ('AIN', ETIQUETAS_INDICADORES.get('AIN', 'Activos Improductivos Netos')),
        ('CAR_ACT', ETIQUETAS_INDICADORES.get('CAR_ACT', 'Cartera / Activos')),
        ('INV_ACT', ETIQUETAS_INDICADORES.get('INV_ACT', 'Inversiones / Activos')),
    ],
    'M - Management y Eficiencia': [
        ('GO_MNF', ETIQUETAS_INDICADORES.get('GO_MNF', 'Gastos Op / Margen Neto Financiero')),
        ('GO_ACT', ETIQUETAS_INDICADORES.get('GO_ACT', 'Gastos Op / Activo Promedio')),
        ('GP_ACT', ETIQUETAS_INDICADORES.get('GP_ACT', 'Gastos Personal / Activo Promedio')),
        ('AP_PC', ETIQUETAS_INDICADORES.get('AP_PC', 'Activos Productivos / Pasivos Costo')),
    ],
    'E - Earnings (Rentabilidad)': [
        ('ROE', ETIQUETAS_INDICADORES.get('ROE', 'ROE')),
        ('ROA', ETIQUETAS_INDICADORES.get('ROA', 'ROA')),
        ('DEP_BRECHA', ETIQUETAS_INDICADORES.get('DEP_BRECHA', 'Depositos Brecha')),
        ('DEP_SPREAD', ETIQUETAS_INDICADORES.get('DEP_SPREAD', 'Depositos Spread')),
    ],
    'L - Liquidez': [
        ('LIQ', ETIQUETAS_INDICADORES.get('LIQ', 'Liquidez')),
    ],
}

# Configuracion de escalas de colores por indicador
ESCALAS_COLORES_HEATMAP = {
    # Indicadores donde mayor es mejor (verde alto, rojo bajo)
    'SOL': 'RdYlGn',          # Solvencia: mayor es mejor
    'ROA': 'RdYlGn',          # ROA: mayor es mejor
    'ROE': 'RdYlGn',          # ROE: mayor es mejor
    'LIQ': 'RdYlGn',          # Liquidez: mayor es mejor
    'AP_PC': 'RdYlGn',        # Activos Productivos / Pasivos con Costo: mayor es mejor
    'CAR_ACT': 'RdYlGn',      # Cartera / Activos: mayor es mejor

    # Cobertura: mayor es mejor
    'COB_TOT': 'RdYlGn',
    'COB_CONS': 'RdYlGn',
    'COB_INMOB': 'RdYlGn',
    'COB_INMOB_VIP': 'RdYlGn',
    'COB_VIS': 'RdYlGn',
    'COB_MICRO': 'RdYlGn',
    'COB_EDU': 'RdYlGn',
    'COB_PROD': 'RdYlGn',
    'COB_INV_PUB': 'RdYlGn',
    'COB_COM_PRIO': 'RdYlGn',
    'COB_CONS_PRIO': 'RdYlGn',

    # Indicadores donde menor es mejor (rojo alto, verde bajo)
    'AIN': 'RdYlGn_r',        # Activos Improductivos: menor es mejor
    'GO_MNF': 'RdYlGn_r',     # Gastos Op. / MNF: menor es mejor
    'GO_ACT': 'RdYlGn_r',     # Gastos Op. / Activos: menor es mejor
    'GP_ACT': 'RdYlGn_r',     # Gastos Personal: menor es mejor

    # Morosidad: menor es mejor
    'MOR_TOT': 'RdYlGn_r',
    'MOR_CONS': 'RdYlGn_r',
    'MOR_INMOB': 'RdYlGn_r',
    'MOR_INMOB_VIP': 'RdYlGn_r',
    'MOR_VIS': 'RdYlGn_r',
    'MOR_MICRO': 'RdYlGn_r',
    'MOR_EDU': 'RdYlGn_r',
    'MOR_PROD': 'RdYlGn_r',
    'MOR_INV_PUB': 'RdYlGn_r',

    # Indicadores neutros
    'INV_ACT': 'Blues',       # Inversiones / Activos: neutro
    'DEP_BRECHA': 'Blues',    # Depositos Brecha: neutro
    'DEP_SPREAD': 'Blues',    # Depositos Spread: neutro

    # Participacion: neutro (distribución)
    'PART_CONS': 'Blues',
    'PART_INMOB': 'Blues',
    'PART_INMOB_VIP': 'Blues',
    'PART_VIS': 'Blues',
    'PART_MICRO': 'Blues',
    'PART_EDU': 'Blues',
    'PART_PROD': 'Blues',
    'PART_INV_PUB': 'Blues',
}

# Rangos de referencia para escalas de color
RANGOS_HEATMAP = {
    # Capital
    'SOL': [0, 20],               # Solvencia 0-20%

    # Rentabilidad
    'ROA': [-5, 5],               # ROA -5% a 5%
    'ROE': [-20, 30],             # ROE -20% a 30%
    'DEP_BRECHA': [0, 10],        # Depositos Brecha 0-10%
    'DEP_SPREAD': [0, 10],        # Depositos Spread 0-10%

    # Liquidez
    'LIQ': [0, 50],               # Liquidez 0-50%

    # Calidad de Activos
    'AIN': [0, 40],               # Act. Improductivos 0-40%
    'CAR_ACT': [0, 100],          # Cartera / Activos 0-100%
    'INV_ACT': [0, 50],           # Inversiones / Activos 0-50%

    # Morosidad (todas con el mismo rango)
    'MOR_TOT': [0, 10],
    'MOR_CONS': [0, 10],
    'MOR_INMOB': [0, 10],
    'MOR_INMOB_VIP': [0, 10],
    'MOR_VIS': [0, 10],
    'MOR_MICRO': [0, 10],
    'MOR_EDU': [0, 10],
    'MOR_PROD': [0, 10],
    'MOR_INV_PUB': [0, 10],

    # Cobertura (todas con el mismo rango)
    'COB_TOT': [0, 300],
    'COB_CONS': [0, 300],
    'COB_INMOB': [0, 300],
    'COB_INMOB_VIP': [0, 300],
    'COB_VIS': [0, 300],
    'COB_MICRO': [0, 300],
    'COB_EDU': [0, 300],
    'COB_PROD': [0, 300],
    'COB_INV_PUB': [0, 300],
    'COB_COM_PRIO': [0, 300],
    'COB_CONS_PRIO': [0, 300],

    # Participacion (suman 100%)
    'PART_CONS': [0, 100],
    'PART_INMOB': [0, 100],
    'PART_INMOB_VIP': [0, 100],
    'PART_VIS': [0, 100],
    'PART_MICRO': [0, 100],
    'PART_EDU': [0, 100],
    'PART_PROD': [0, 100],
    'PART_INV_PUB': [0, 100],

    # Eficiencia
    'AP_PC': [80, 120],           # Act. Prod. / Pas. Costo 80-120%
    'GO_MNF': [0, 200],           # Gastos Op. / MNF 0-200%
    'GO_ACT': [0, 10],            # Gastos Op. / Activos 0-10%
    'GP_ACT': [0, 5],             # Gastos Personal 0-5%
}


# =============================================================================
# FUNCIONES DE DATOS
# =============================================================================

@st.cache_data
def obtener_fecha_disponible(df: pd.DataFrame, codigo: str, fecha_objetivo) -> pd.Timestamp:
    """
    Obtiene la fecha mas reciente disponible para un indicador.
    Si no existe dato para la fecha objetivo, busca el mes anterior.

    Esto maneja el caso del indice de solvencia que tiene rezago de 1 mes.
    """
    # Intentar con fecha objetivo
    df_fecha = df[(df['codigo'] == codigo) & (df['fecha'] == fecha_objetivo)]

    if not df_fecha.empty:
        return fecha_objetivo

    # Si no hay datos, buscar la fecha mas cercana anterior
    df_codigo = df[df['codigo'] == codigo]
    fechas_disponibles = df_codigo['fecha'].sort_values(ascending=False)

    for fecha in fechas_disponibles:
        if fecha <= fecha_objetivo:
            return fecha

    # Si no hay ninguna fecha anterior, retornar la mas reciente
    return fechas_disponibles.iloc[0] if len(fechas_disponibles) > 0 else fecha_objetivo


@st.cache_data
def obtener_ranking_indicador(df: pd.DataFrame, codigo: str, fecha, excluir_bancos: list = None) -> pd.DataFrame:
    """Obtiene ranking de bancos para un indicador en una fecha."""
    # Obtener fecha disponible (maneja rezago)
    fecha_real = obtener_fecha_disponible(df, codigo, fecha)

    df_filtrado = df[(df['codigo'] == codigo) & (df['fecha'] == fecha_real)].copy()

    # Excluir bancos si se especifica
    if excluir_bancos:
        df_filtrado = df_filtrado[~df_filtrado['banco'].isin(excluir_bancos)]

    df_filtrado['valor_pct'] = df_filtrado['valor'] * 100
    df_filtrado = df_filtrado.sort_values('valor', ascending=False)
    return df_filtrado[['banco', 'valor', 'valor_pct']], fecha_real


@st.cache_data
def obtener_evolucion_indicador(df: pd.DataFrame, codigo: str, bancos: list) -> pd.DataFrame:
    """Obtiene evolucion temporal de un indicador para varios bancos."""
    df_filtrado = df[(df['codigo'] == codigo) & (df['banco'].isin(bancos))].copy()
    df_filtrado = df_filtrado.sort_values(['banco', 'fecha'])
    df_filtrado['valor_pct'] = df_filtrado['valor'] * 100
    return df_filtrado


@st.cache_data
@st.cache_data
def obtener_heatmap_indicador(df: pd.DataFrame, codigo: str, fecha_inicio=None, fecha_fin=None) -> pd.DataFrame:
    """Obtiene datos para heatmap de un indicador (bancos x meses)."""
    df_filtrado = df[df['codigo'] == codigo].copy()

    # Filtrar por rango de fechas si se especifica
    if fecha_inicio is not None:
        df_filtrado = df_filtrado[df_filtrado['fecha'] >= fecha_inicio]
    if fecha_fin is not None:
        df_filtrado = df_filtrado[df_filtrado['fecha'] <= fecha_fin]

    if df_filtrado.empty:
        return pd.DataFrame()

    # Crear columna de periodo (Año-Mes)
    df_filtrado['periodo'] = df_filtrado['fecha'].dt.strftime('%Y-%m')

    # Pivot: bancos x periodos
    heatmap_data = df_filtrado.pivot(index='banco', columns='periodo', values='valor')

    # Ordenar por tamaño de banco (activos)
    try:
        df_balance, _ = cargar_balance()
        # Obtener fecha mas reciente disponible
        fecha_max = df_balance['fecha'].max()
        # Filtrar activos totales (codigo '1')
        df_activos = df_balance[
            (df_balance['codigo'] == '1') &
            (df_balance['fecha'] == fecha_max)
        ][['banco', 'valor']].copy()
        df_activos = df_activos.set_index('banco')

        # Ordenar bancos del heatmap por activos (de menor a mayor, para que mayor quede arriba)
        bancos_ordenados = df_activos.sort_values('valor', ascending=True).index
        bancos_en_heatmap = [b for b in bancos_ordenados if b in heatmap_data.index]

        # Reordenar heatmap
        if bancos_en_heatmap:
            heatmap_data = heatmap_data.reindex(bancos_en_heatmap)
    except Exception as e:
        # Si falla la carga de balance, ordenar por ultimo periodo
        if len(heatmap_data.columns) > 0:
            ultima_col = heatmap_data.columns[-1]
            heatmap_data = heatmap_data.sort_values(ultima_col, ascending=False, na_position='last')

    return heatmap_data * 100  # Convertir a porcentaje


# =============================================================================
# VISUALIZACIONES
# =============================================================================

def crear_grafico_evolucion(df: pd.DataFrame, codigo: str, bancos: list, nombre_indicador: str, fecha_inicio=None):
    """Crea grafico de evolucion temporal de un indicador."""
    df_evol = obtener_evolucion_indicador(df, codigo, bancos)

    if df_evol.empty:
        st.warning("No hay datos disponibles para los bancos seleccionados")
        return

    # Filtrar por fecha de inicio si se especifica
    if fecha_inicio is not None:
        df_evol = df_evol[df_evol['fecha'] >= fecha_inicio]

    # Crear mapeo de colores para los bancos seleccionados
    color_map = {banco: obtener_color_banco(banco) for banco in bancos}

    fig = px.line(
        df_evol,
        x='fecha',
        y='valor_pct',
        color='banco',
        title=f"Evolucion: {nombre_indicador}",
        labels={'fecha': 'Fecha', 'valor_pct': 'Valor (%)', 'banco': 'Banco'},
        color_discrete_map=color_map,
    )

    fig.update_layout(
        height=450,
        legend=dict(orientation='h', yanchor='bottom', y=-0.3, xanchor='center', x=0.5),
        hovermode='x unified',
    )

    st.plotly_chart(fig, use_container_width=True)


def crear_ranking_barras(df: pd.DataFrame, codigo: str, fecha, nombre_indicador: str,
                         excluir_bancos: list = None):
    """Crea ranking de barras horizontales para un indicador."""
    df_ranking, fecha_real = obtener_ranking_indicador(df, codigo, fecha, excluir_bancos)

    if df_ranking.empty:
        st.warning("No hay datos disponibles")
        return

    df_top = df_ranking  # Mostrar todos los bancos

    # Usar colores consistentes por banco
    colors = [obtener_color_banco(banco) for banco in df_top['banco']]

    fig = go.Figure(go.Bar(
        x=df_top['valor_pct'],
        y=df_top['banco'],
        orientation='h',
        marker=dict(color=colors),
        text=df_top['valor_pct'].apply(lambda x: f"{x:.1f}%"),
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>Valor: %{x:.1f}%<extra></extra>'
    ))

    fig.update_layout(
        title=f"Ranking: {nombre_indicador}",
        xaxis_title='Valor (%)',
        yaxis_title='',
        height=max(400, len(df_top) * 25),
        showlegend=False,
        yaxis=dict(categoryorder='total ascending'),
    )

    st.plotly_chart(fig, use_container_width=True)

    # Mostrar nota si la fecha real es diferente a la solicitada
    if fecha_real != fecha:
        st.info(f"ℹ️ Datos de {fecha_real.strftime('%B %Y')} (fecha mas reciente disponible)")

    # Mostrar nota si se excluyeron bancos
    if excluir_bancos:
        st.caption(f"⚠️ Excluidos del ranking: {', '.join(excluir_bancos)} (valores atípicos)")


def crear_heatmap_indicador(df: pd.DataFrame, codigo: str, nombre_indicador: str, fecha_inicio=None, fecha_fin=None):
    """Crea heatmap de evolucion mensual de un indicador."""
    heatmap_data = obtener_heatmap_indicador(df, codigo, fecha_inicio, fecha_fin)

    if heatmap_data.empty:
        st.warning("No hay datos suficientes para el heatmap en el rango seleccionado")
        return

    # Obtener escala de colores y rango para este indicador
    colorscale = ESCALAS_COLORES_HEATMAP.get(codigo, 'RdYlGn')
    rango = RANGOS_HEATMAP.get(codigo, None)

    # Determinar zmid (punto medio de la escala)
    zmid = None
    if rango:
        if codigo in ['ROA', 'ROE']:
            # Para ROA y ROE, centrar en 0
            zmid = 0
        else:
            # Para otros, usar punto medio del rango
            zmid = (rango[0] + rango[1]) / 2

    # Crear heatmap
    fig = go.Figure(data=go.Heatmap(
        z=heatmap_data.values,
        x=heatmap_data.columns,
        y=heatmap_data.index,
        colorscale=colorscale,
        zmid=zmid,
        zmin=rango[0] if rango else None,
        zmax=rango[1] if rango else None,
        hovertemplate='Banco: %{y}<br>Periodo: %{x}<br>Valor: %{z:.1f}%<extra></extra>',
    ))

    fig.update_layout(
        title=f"Evolucion Mensual: {nombre_indicador} (%)",
        height=max(400, len(heatmap_data) * 22),
        xaxis_title='Periodo (Año-Mes)',
        yaxis_title='Banco',
        xaxis={'tickangle': -45},
    )

    st.plotly_chart(fig, use_container_width=True)


# =============================================================================
# MAIN
# =============================================================================

def main():
    """Funcion principal del modulo CAMEL."""
    st.title("📈 Indicadores CAMEL")

    # Cargar datos
    try:
        df_camel, calidad = cargar_camel()
    except FileNotFoundError as e:
        st.error(f"No se encontro el archivo de datos CAMEL: {e}")
        st.info("Ejecuta `python procesar_camel.py` para generar los datos")
        return

    # Sidebar
    st.sidebar.header("Filtros")

    fechas = obtener_fechas_disponibles(df_camel)
    fecha_default = fechas[0] if fechas else None
    fecha_seleccionada = st.sidebar.selectbox(
        "Fecha de analisis",
        options=fechas,
        index=0 if fechas else None,
        format_func=lambda x: x.strftime('%B %Y') if pd.notna(x) else str(x)
    )

    bancos_disponibles = sorted(df_camel['banco'].unique())

    st.sidebar.markdown("---")
    st.sidebar.markdown(f"**Indicadores:** {calidad['indicadores_unicos']}")
    st.sidebar.markdown(f"**Bancos:** {calidad['bancos']}")
    st.sidebar.markdown(f"**Registros:** {calidad['registros_limpios']:,}")

    # Tabs principales
    tab1, tab3, tab4 = st.tabs([
        "📊 Analisis por Indicador",
        "📈 Evolucion Temporal",
        "🗺️ Heatmap Mensual"
    ])

    # Tab 1: Analisis por Indicador
    with tab1:
        col1, col2 = st.columns([1, 2])

        with col1:
            # Selector de categoria
            categorias = list(INDICADORES_PRINCIPALES.keys())
            # Preseleccionar "A - Morosidad por Cartera"
            default_cat_idx = categorias.index('A - Morosidad por Cartera') if 'A - Morosidad por Cartera' in categorias else 0
            categoria_sel = st.selectbox("Categoria", categorias, index=default_cat_idx)

            # Selector de indicador
            indicadores_cat = INDICADORES_PRINCIPALES[categoria_sel]
            indicador_opciones = {nombre: codigo for codigo, nombre in indicadores_cat}
            indicador_nombre = st.selectbox("Indicador", list(indicador_opciones.keys()))
            indicador_codigo = indicador_opciones[indicador_nombre]

        with col2:
            # Determinar si excluir bancos con valores atípicos (para indicadores de cobertura)
            excluir_bancos = None
            if indicador_codigo == 'COB_TOT':
                excluir_bancos = ['Citibank', 'Coopnacional']

            crear_ranking_barras(df_camel, indicador_codigo, fecha_seleccionada,
                                indicador_nombre, excluir_bancos)

    # Tab 3: Evolucion Temporal
    with tab3:
        col1, col2 = st.columns([1, 3])

        with col1:
            # Selector de categoria
            categorias_evol = list(INDICADORES_PRINCIPALES.keys())
            # Preseleccionar "A - Morosidad por Cartera"
            default_cat_evol_idx = categorias_evol.index('A - Morosidad por Cartera') if 'A - Morosidad por Cartera' in categorias_evol else 0
            categoria_evol = st.selectbox("Categoria", categorias_evol, index=default_cat_evol_idx, key='cat_evol')

            # Selector de indicador
            indicadores_evol = INDICADORES_PRINCIPALES[categoria_evol]
            indicador_opciones_evol = {nombre: codigo for codigo, nombre in indicadores_evol}
            indicador_nombre_evol = st.selectbox("Indicador", list(indicador_opciones_evol.keys()), key='ind_evol')
            indicador_codigo_evol = indicador_opciones_evol[indicador_nombre_evol]

            # Multiselect de bancos
            bancos_evol = st.multiselect(
                "Bancos a comparar",
                bancos_disponibles,
                default=['Pichincha', 'Guayaquil', 'Pacifico'] if all(b in bancos_disponibles for b in ['Pichincha', 'Guayaquil', 'Pacifico']) else bancos_disponibles[:3],
                max_selections=8
            )

            # Fecha de inicio (predeterminado: Enero 2015)
            st.markdown("---")
            fecha_min_sistema = df_camel['fecha'].min()
            fecha_max_sistema = df_camel['fecha'].max()

            # Determinar fecha de inicio por defecto (Enero 2015 o la mas reciente si no existe)
            fecha_default_inicio = pd.Timestamp(year=2015, month=1, day=1)
            if fecha_default_inicio < fecha_min_sistema:
                fecha_default_inicio = fecha_min_sistema

            fecha_inicio_evol = st.date_input(
                "Fecha de inicio",
                value=fecha_default_inicio,
                min_value=fecha_min_sistema,
                max_value=fecha_max_sistema,
                key='fecha_inicio_evol'
            )
            fecha_inicio_evol = pd.Timestamp(fecha_inicio_evol)

        with col2:
            if bancos_evol:
                crear_grafico_evolucion(df_camel, indicador_codigo_evol, bancos_evol, indicador_nombre_evol, fecha_inicio_evol)
            else:
                st.info("Selecciona al menos un banco para ver la evolucion")

    # Tab 4: Heatmap Mensual
    with tab4:
        col1, col2 = st.columns([1, 3])

        with col1:
            # Selector de categoria
            categorias_heat = list(INDICADORES_PRINCIPALES.keys())
            # Preseleccionar "A - Morosidad por Cartera"
            default_cat_heat_idx = categorias_heat.index('A - Morosidad por Cartera') if 'A - Morosidad por Cartera' in categorias_heat else 0
            categoria_heat = st.selectbox("Categoria", categorias_heat, index=default_cat_heat_idx, key='cat_heat')

            # Selector de indicador
            indicadores_heat = INDICADORES_PRINCIPALES[categoria_heat]
            indicador_opciones_heat = {nombre: codigo for codigo, nombre in indicadores_heat}
            indicador_nombre_heat = st.selectbox("Indicador", list(indicador_opciones_heat.keys()), key='ind_heat')
            indicador_codigo_heat = indicador_opciones_heat[indicador_nombre_heat]

            st.markdown("---")
            st.subheader("Rango de Fechas")

            # Obtener fechas minima y maxima del dataset
            fecha_min = df_camel['fecha'].min()
            fecha_max = df_camel['fecha'].max()

            # Selector de año inicial y final
            anos_disponibles = sorted(df_camel['fecha'].dt.year.unique())

            col_a, col_b = st.columns(2)
            with col_a:
                ano_inicio = st.selectbox(
                    "Año inicio",
                    anos_disponibles,
                    index=max(0, len(anos_disponibles) - 5) if len(anos_disponibles) > 5 else 0,
                    key='ano_inicio_heat'
                )
            with col_b:
                ano_fin = st.selectbox(
                    "Año fin",
                    anos_disponibles,
                    index=len(anos_disponibles) - 1,
                    key='ano_fin_heat'
                )

            # Selector de mes inicial y final
            meses = [
                ('Enero', 1), ('Febrero', 2), ('Marzo', 3), ('Abril', 4),
                ('Mayo', 5), ('Junio', 6), ('Julio', 7), ('Agosto', 8),
                ('Septiembre', 9), ('Octubre', 10), ('Noviembre', 11), ('Diciembre', 12)
            ]
            meses_nombres = [m[0] for m in meses]
            meses_numeros = [m[1] for m in meses]

            col_c, col_d = st.columns(2)
            with col_c:
                mes_inicio_idx = st.selectbox(
                    "Mes inicio",
                    range(len(meses)),
                    index=0,
                    format_func=lambda x: meses_nombres[x],
                    key='mes_inicio_heat'
                )
                mes_inicio = meses_numeros[mes_inicio_idx]
            with col_d:
                mes_fin_idx = st.selectbox(
                    "Mes fin",
                    range(len(meses)),
                    index=11,
                    format_func=lambda x: meses_nombres[x],
                    key='mes_fin_heat'
                )
                mes_fin = meses_numeros[mes_fin_idx]

            # Construir fechas de inicio y fin
            fecha_inicio_heat = pd.Timestamp(year=ano_inicio, month=mes_inicio, day=1)
            fecha_fin_heat = pd.Timestamp(year=ano_fin, month=mes_fin, day=1)

            # Validar que fecha_inicio <= fecha_fin
            if fecha_inicio_heat > fecha_fin_heat:
                st.warning("La fecha de inicio debe ser anterior a la fecha de fin")
                fecha_inicio_heat, fecha_fin_heat = fecha_fin_heat, fecha_inicio_heat

        with col2:
            crear_heatmap_indicador(
                df_camel,
                indicador_codigo_heat,
                indicador_nombre_heat,
                fecha_inicio_heat,
                fecha_fin_heat
            )


if __name__ == "__main__":
    main()
