# -*- coding: utf-8 -*-
"""
Componentes graficos reutilizables para el dashboard.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import List, Optional, Dict, Any
from pathlib import Path
import sys

# Agregar path para imports
sys.path.append(str(Path(__file__).parent.parent))
from config.indicator_mapping import COLORES_BANCOS, obtener_color_banco


# =============================================================================
# COLORES Y ESTILOS
# =============================================================================

COLORES = {
    'primario': '#1a365d',
    'secundario': '#2c5282',
    'acento': '#3182ce',
    'exito': '#38a169',
    'advertencia': '#dd6b20',
    'error': '#e53e3e',
    'neutro': '#718096',
    'fondo': '#f7fafc',
}

# DEPRECATED: Usar COLORES_BANCOS desde config.indicator_mapping
PALETA_BANCOS = px.colors.qualitative.Set2 + px.colors.qualitative.Pastel1

LAYOUT_BASE = {
    'font': {'family': 'Inter, sans-serif'},
    'paper_bgcolor': 'white',
    'plot_bgcolor': 'white',
    'margin': {'l': 10, 'r': 10, 't': 40, 'b': 10},
}


# =============================================================================
# FUNCIONES DE COLORES
# =============================================================================

def obtener_colores_para_bancos(bancos: List[str]) -> Dict[str, str]:
    """Obtiene un diccionario de colores para una lista de bancos.

    Args:
        bancos: Lista de nombres de bancos

    Returns:
        Diccionario {banco: color}
    """
    return {banco: obtener_color_banco(banco) for banco in bancos}


def aplicar_colores_bancos(fig, bancos: List[str], trace_index: int = 0):
    """Aplica colores consistentes a las trazas de un gráfico Plotly.

    Args:
        fig: Figura de Plotly
        bancos: Lista de nombres de bancos en orden de aparición
        trace_index: Índice de la traza a modificar (default: 0 para todas)
    """
    colores = [obtener_color_banco(banco) for banco in bancos]

    if trace_index == 0:
        # Aplicar a todas las trazas
        for i, trace in enumerate(fig.data):
            if i < len(colores):
                trace.marker.color = colores[i]
    else:
        # Aplicar a una traza específica
        fig.data[trace_index].marker.color = colores


# =============================================================================
# TARJETAS KPI
# =============================================================================

def render_kpi_card(
    valor: str,
    label: str,
    delta: Optional[float] = None,
    delta_label: str = "",
    color: str = COLORES['acento']
):
    """
    Renderiza una tarjeta KPI con estilos personalizados.
    """
    delta_html = ""
    if delta is not None:
        clase = "positive" if delta >= 0 else "negative"
        signo = "+" if delta >= 0 else ""
        delta_color = COLORES['exito'] if delta >= 0 else COLORES['error']
        delta_html = f'<div style="color: {delta_color}; font-size: 0.85rem; margin-top: 4px;">{signo}{delta:.1f}% {delta_label}</div>'

    st.markdown(f"""
        <div style="
            background: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%);
            border-radius: 12px;
            padding: 1.2rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            border-left: 4px solid {color};
            margin-bottom: 1rem;
        ">
            <div style="font-size: 1.8rem; font-weight: 700; color: #1a365d;">{valor}</div>
            <div style="font-size: 0.8rem; color: #718096; text-transform: uppercase; letter-spacing: 0.5px;">{label}</div>
            {delta_html}
        </div>
    """, unsafe_allow_html=True)


def render_kpi_row(kpis: List[Dict[str, Any]]):
    """
    Renderiza una fila de KPIs.

    Args:
        kpis: Lista de dicts con keys: valor, label, delta (opcional), color (opcional)
    """
    cols = st.columns(len(kpis))
    for col, kpi in zip(cols, kpis):
        with col:
            render_kpi_card(
                valor=kpi['valor'],
                label=kpi['label'],
                delta=kpi.get('delta'),
                delta_label=kpi.get('delta_label', ''),
                color=kpi.get('color', COLORES['acento'])
            )


# =============================================================================
# GRAFICOS DE RANKING
# =============================================================================

def crear_ranking_barras(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    titulo: str = "",
    color_col: Optional[str] = None,
    formato_valor: str = "${:,.0f}M",
    altura: int = 400,
    usar_colores_bancos: bool = True
) -> go.Figure:
    """
    Crea grafico de barras horizontales para ranking.

    Args:
        df: DataFrame con datos
        x_col: Columna para eje X (valores)
        y_col: Columna para eje Y (labels, típicamente bancos)
        titulo: Título del gráfico
        color_col: Columna para escala de colores (opcional)
        formato_valor: Formato para mostrar valores
        altura: Altura del gráfico
        usar_colores_bancos: Si True, usa colores consistentes por banco
    """
    df_sorted = df.sort_values(x_col, ascending=True)

    # Determinar colores
    if usar_colores_bancos and y_col == 'banco':
        # Usar colores consistentes por banco
        colors = [obtener_color_banco(banco) for banco in df_sorted[y_col]]
        marker_dict = dict(color=colors)
    elif color_col:
        colors = df_sorted[color_col]
        marker_dict = dict(color=colors, colorscale='Blues')
    else:
        colors = df_sorted[x_col]
        marker_dict = dict(color=colors, colorscale='Blues')

    fig = go.Figure(go.Bar(
        y=df_sorted[y_col],
        x=df_sorted[x_col],
        orientation='h',
        marker=marker_dict,
        text=[formato_valor.format(v) for v in df_sorted[x_col]],
        textposition='outside',
        hovertemplate="<b>%{y}</b><br>Valor: %{x:,.2f}<extra></extra>"
    ))

    fig.update_layout(
        **LAYOUT_BASE,
        title=titulo,
        height=altura,
        xaxis_title="",
        yaxis_title="",
        yaxis=dict(categoryorder='total ascending'),
        showlegend=False
    )

    return fig


# =============================================================================
# TREEMAP
# =============================================================================

def crear_treemap(
    df: pd.DataFrame,
    path_col: str = None,
    values_col: str = None,
    color_col: Optional[str] = None,
    titulo: str = "",
    altura: int = 450,
    jerarquico: bool = False
) -> go.Figure:
    """
    Crea un treemap para visualizar composicion.

    Si jerarquico=True, espera un DataFrame con columnas 'labels', 'parents', 'values'
    Si jerarquico=False, usa path_col, values_col tradicionales
    """
    df_clean = df.copy()

    # Modo jerarquico (con drill-down)
    if jerarquico:
        # Validar que existan las columnas necesarias
        required_cols = ['labels', 'parents', 'values']
        if not all(col in df_clean.columns for col in required_cols):
            fig = go.Figure()
            fig.add_annotation(
                text="Estructura de datos incorrecta",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16)
            )
            fig.update_layout(height=altura, title=titulo)
            return fig

        df_clean = df_clean.dropna(subset=['values'])
        df_clean = df_clean[df_clean['values'] > 0]

        if df_clean.empty:
            fig = go.Figure()
            fig.add_annotation(
                text="No hay datos disponibles",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16)
            )
            fig.update_layout(height=altura, title=titulo)
            return fig

        labels = df_clean['labels'].tolist()
        parents = df_clean['parents'].tolist()
        values = df_clean['values'].tolist()

        # Usar IDs unicos si existen, para evitar conflictos con nombres duplicados
        if 'id' in df_clean.columns:
            ids = df_clean['id'].tolist()
        else:
            ids = None

        # Colores basados en participacion si existe
        if 'participacion' in df_clean.columns:
            colors = df_clean['participacion'].tolist()
        else:
            colors = values

        # Crear customdata para hover
        customdata = []
        for i, row in df_clean.iterrows():
            if row['parents'] == '':  # Es un banco (nivel raiz)
                if 'participacion' in df_clean.columns:
                    customdata.append([row['participacion']])
                else:
                    customdata.append([0])
            else:  # Es una cuenta (niveles 2 o 3)
                customdata.append([0])

        # Template de texto - mostrar label y valor
        texttemplate = "%{label}<br>$%{value:,.0f}M"

        # Hover template personalizado
        if 'participacion' in df_clean.columns:
            hovertemplate = "<b>%{label}</b><br>Valor: $%{value:,.0f}M<br>Participación: %{customdata[0]:.1f}%<extra></extra>"
        else:
            hovertemplate = "<b>%{label}</b><br>Valor: $%{value:,.0f}M<extra></extra>"

        fig = go.Figure(go.Treemap(
            labels=labels,
            ids=ids,
            parents=parents,
            values=values,
            marker=dict(
                colors=colors,
                colorscale='Blues',
                showscale=False,
                line=dict(width=2, color='white')
            ),
            texttemplate=texttemplate,
            customdata=customdata if 'participacion' in df_clean.columns else None,
            hovertemplate=hovertemplate,
            branchvalues="total"
        ))

    else:
        # Modo tradicional (sin drill-down)
        df_clean = df_clean.dropna(subset=[values_col, path_col])
        df_clean = df_clean[df_clean[values_col] > 0]

        if df_clean.empty:
            fig = go.Figure()
            fig.add_annotation(
                text="No hay datos disponibles",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16)
            )
            fig.update_layout(height=altura, title=titulo)
            return fig

        labels = df_clean[path_col].tolist()
        parents = [''] * len(labels)
        values = df_clean[values_col].tolist()

        if color_col and color_col in df_clean.columns:
            colors = df_clean[color_col].tolist()
        else:
            colors = values

        texts = []
        for i, row in df_clean.iterrows():
            texto = f"<b>{row[path_col]}</b><br>${row[values_col]:,.0f}M"
            if color_col and color_col in df_clean.columns:
                texto += f"<br>{row[color_col]:.1f}%"
            texts.append(texto)

        fig = go.Figure(go.Treemap(
            labels=labels,
            parents=parents,
            values=values,
            marker=dict(
                colors=colors,
                colorscale='Blues',
                showscale=True
            ),
            text=texts,
            textposition='middle center',
            hovertemplate="<b>%{label}</b><br>Valor: $%{value:,.0f}M<extra></extra>"
        ))

    fig.update_layout(
        **LAYOUT_BASE,
        title=titulo,
        height=altura,
    )

    return fig


# =============================================================================
# GRAFICO DE LINEAS (SERIES TEMPORALES)
# =============================================================================

def crear_linea_temporal(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    color_col: Optional[str] = None,
    titulo: str = "",
    y_label: str = "Valor",
    altura: int = 400,
    mostrar_area: bool = False,
    usar_colores_bancos: bool = True
) -> go.Figure:
    """
    Crea grafico de lineas para series temporales.

    Args:
        df: DataFrame con datos
        x_col: Columna para eje X (fechas)
        y_col: Columna para eje Y (valores)
        color_col: Columna para agrupar líneas (típicamente 'banco')
        titulo: Título del gráfico
        y_label: Etiqueta del eje Y
        altura: Altura del gráfico
        mostrar_area: Si True, rellena área bajo la curva
        usar_colores_bancos: Si True, usa colores consistentes por banco
    """
    if color_col:
        # Usar colores consistentes si color_col es 'banco'
        if usar_colores_bancos and color_col == 'banco':
            # Obtener bancos únicos en orden de aparición
            bancos = df[color_col].unique().tolist()
            color_map = obtener_colores_para_bancos(bancos)

            fig = px.line(
                df,
                x=x_col,
                y=y_col,
                color=color_col,
                markers=True,
                line_shape='spline',
                color_discrete_map=color_map,
            )
        else:
            fig = px.line(
                df,
                x=x_col,
                y=y_col,
                color=color_col,
                markers=True,
                line_shape='spline',
                color_discrete_sequence=PALETA_BANCOS,
            )
    else:
        fig = px.line(
            df,
            x=x_col,
            y=y_col,
            markers=True,
            line_shape='spline',
        )
        if mostrar_area:
            fig.update_traces(fill='tozeroy', line_color=COLORES['acento'])

    fig.update_layout(
        **LAYOUT_BASE,
        title=titulo,
        height=altura,
        xaxis_title="",
        yaxis_title=y_label,
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    fig.update_xaxes(showgrid=True, gridcolor='#f0f0f0')
    fig.update_yaxes(showgrid=True, gridcolor='#f0f0f0')

    return fig


# =============================================================================
# GRAFICO RADAR (CAMEL)
# =============================================================================

def crear_radar_camel(
    valores: Dict[str, float],
    titulo: str = "",
    valores_benchmark: Optional[Dict[str, float]] = None,
    altura: int = 400
) -> go.Figure:
    """
    Crea grafico de radar para indicadores CAMEL.

    Args:
        valores: Dict con keys C, A, M, E, L y valores 0-100
        valores_benchmark: Opcional, valores de referencia para comparar
    """
    categorias = ['Capital (C)', 'Activos (A)', 'Management (M)', 'Earnings (E)', 'Liquidity (L)']
    keys = ['C', 'A', 'M', 'E', 'L']

    # Valores del banco
    r_valores = [valores.get(k, 0) for k in keys]
    r_valores.append(r_valores[0])  # Cerrar el poligono
    categorias_cerradas = categorias + [categorias[0]]

    fig = go.Figure()

    # Agregar benchmark si existe
    if valores_benchmark:
        r_bench = [valores_benchmark.get(k, 0) for k in keys]
        r_bench.append(r_bench[0])
        fig.add_trace(go.Scatterpolar(
            r=r_bench,
            theta=categorias_cerradas,
            fill='toself',
            fillcolor='rgba(49, 130, 206, 0.1)',
            line=dict(color=COLORES['acento'], width=1, dash='dash'),
            name='Promedio Sistema'
        ))

    # Agregar valores del banco
    fig.add_trace(go.Scatterpolar(
        r=r_valores,
        theta=categorias_cerradas,
        fill='toself',
        fillcolor='rgba(56, 161, 105, 0.3)',
        line=dict(color=COLORES['exito'], width=2),
        name='Banco'
    ))

    fig.update_layout(
        **LAYOUT_BASE,
        title=titulo,
        height=altura,
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )
        ),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5
        )
    )

    return fig


# =============================================================================
# GAUGE (INDICADOR TIPO VELOCIMETRO)
# =============================================================================

def crear_gauge(
    valor: float,
    titulo: str = "",
    min_val: float = 0,
    max_val: float = 100,
    umbrales: Optional[List[Dict]] = None,
    altura: int = 250
) -> go.Figure:
    """
    Crea indicador tipo gauge (velocimetro).

    Args:
        umbrales: Lista de dicts con 'rango' (tuple) y 'color'
    """
    if umbrales is None:
        umbrales = [
            {'rango': (0, 33), 'color': '#fed7d7'},
            {'rango': (33, 66), 'color': '#fefcbf'},
            {'rango': (66, 100), 'color': '#c6f6d5'},
        ]

    # Determinar color de la barra
    color_barra = COLORES['neutro']
    for umbral in umbrales:
        if umbral['rango'][0] <= valor <= umbral['rango'][1]:
            if umbral['color'] == '#c6f6d5':
                color_barra = COLORES['exito']
            elif umbral['color'] == '#fefcbf':
                color_barra = COLORES['advertencia']
            else:
                color_barra = COLORES['error']

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=valor,
        title={'text': titulo, 'font': {'size': 14}},
        gauge={
            'axis': {'range': [min_val, max_val]},
            'bar': {'color': color_barra},
            'steps': [
                {'range': u['rango'], 'color': u['color']}
                for u in umbrales
            ],
        }
    ))

    fig.update_layout(
        **LAYOUT_BASE,
        height=altura,
    )

    return fig


# =============================================================================
# HEATMAP
# =============================================================================

def crear_heatmap(
    df: pd.DataFrame,
    titulo: str = "",
    color_scale: str = 'Blues',
    altura: int = 400,
    mostrar_valores: bool = True
) -> go.Figure:
    """
    Crea heatmap a partir de un DataFrame pivotado.
    """
    fig = px.imshow(
        df,
        color_continuous_scale=color_scale,
        aspect='auto',
    )

    if mostrar_valores:
        fig.update_traces(
            text=df.values,
            texttemplate="%{text:.1f}",
            textfont={"size": 10},
        )

    fig.update_layout(
        **LAYOUT_BASE,
        title=titulo,
        height=altura,
    )

    return fig


# =============================================================================
# SCATTER PLOT (MATRIZ DE POSICIONAMIENTO)
# =============================================================================

def crear_scatter_posicionamiento(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    size_col: str,
    label_col: str,
    x_label: str = "",
    y_label: str = "",
    titulo: str = "",
    altura: int = 500
) -> go.Figure:
    """
    Crea grafico de dispersion para posicionamiento estrategico.
    """
    fig = px.scatter(
        df,
        x=x_col,
        y=y_col,
        size=size_col,
        text=label_col,
        color=size_col,
        color_continuous_scale='Blues',
        size_max=60,
    )

    fig.update_traces(
        textposition='top center',
        textfont=dict(size=10),
        hovertemplate=(
            f"<b>%{{text}}</b><br>"
            f"{x_label}: %{{x:.2f}}<br>"
            f"{y_label}: %{{y:.2f}}<br>"
            f"Tamano: %{{marker.size:,.0f}}<extra></extra>"
        )
    )

    # Agregar lineas de referencia (promedio)
    x_mean = df[x_col].mean()
    y_mean = df[y_col].mean()

    fig.add_hline(y=y_mean, line_dash="dash", line_color=COLORES['neutro'], opacity=0.5)
    fig.add_vline(x=x_mean, line_dash="dash", line_color=COLORES['neutro'], opacity=0.5)

    fig.update_layout(
        **LAYOUT_BASE,
        title=titulo,
        height=altura,
        xaxis_title=x_label,
        yaxis_title=y_label,
    )

    return fig


# =============================================================================
# BARRAS APILADAS (ESTRUCTURA DE BALANCE)
# =============================================================================

def crear_barras_apiladas_100(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    color_col: str,
    titulo: str = "",
    altura: int = 300
) -> go.Figure:
    """
    Crea grafico de barras apiladas al 100%.
    """
    fig = px.bar(
        df,
        x=x_col,
        y=y_col,
        color=color_col,
        barmode='stack',
        color_discrete_sequence=PALETA_BANCOS,
        text_auto='.1f'
    )

    fig.update_layout(
        **LAYOUT_BASE,
        title=titulo,
        height=altura,
        xaxis_title="",
        yaxis_title="Porcentaje (%)",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.3,
            xanchor="center",
            x=0.5
        )
    )

    return fig
