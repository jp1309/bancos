#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Inteligencia Financiera - Banca Ecuatoriana

Dashboard interactivo para análisis del sistema bancario ecuatoriano
con datos históricos desde 2003.

Ejecutar con: streamlit run Inicio.py
"""

import streamlit as st
import json
from pathlib import Path

from dashboard_metadata import resumir_metadata

# =============================================================================
# CONFIGURACION DE PAGINA (debe ser lo primero)
# =============================================================================

st.set_page_config(
    page_title="Sistema BI - Banca Ecuador",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': """
        ## Sistema de Inteligencia Financiera
        Plataforma de análisis del sistema bancario ecuatoriano.

        **Fuente de datos:** Superintendencia de Bancos del Ecuador
        **Periodo:** desde 2003, con actualización mensual
        **Bancos:** cobertura validada en cada actualización
        """
    },
    # Nombre personalizado para la página principal en el sidebar
)

# =============================================================================
# ESTILOS CSS GLOBALES
# =============================================================================

st.markdown("""
<style>
    /* Fuente principal */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Header principal */
    .main-header {
        background: linear-gradient(135deg, #1a365d 0%, #2c5282 50%, #2b6cb0 100%);
        padding: 1.5rem 2rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 40px rgba(26, 54, 93, 0.3);
    }

    .main-header h1 {
        color: white;
        font-size: 2.2rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }

    .main-header p {
        color: rgba(255,255,255,0.85);
        font-size: 1rem;
        margin: 0.5rem 0 0 0;
    }

    /* Tarjetas */
    .card {
        background: linear-gradient(145deg, #ffffff 0%, #f7fafc 100%);
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        border: 1px solid rgba(226, 232, 240, 0.8);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }

    .card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 40px rgba(0,0,0,0.12);
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f7fafc 0%, #edf2f7 100%);
        min-width: 220px !important;
        max-width: 220px !important;
        width: 220px !important;
    }

    /* Ocultar elementos de Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Tabs personalizados */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: #f7fafc;
        padding: 0.5rem;
        border-radius: 12px;
    }

    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 500;
    }

    .stTabs [aria-selected="true"] {
        background: white;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }

    /* Metricas */
    [data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: 700;
        color: #1a365d;
    }

    [data-testid="stMetricLabel"] {
        font-size: 0.85rem;
        color: #718096;
        text-transform: uppercase;
    }

    /* Botones de acceso rapido */
    .quick-access-btn {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 12px;
        text-align: center;
        font-weight: 600;
        text-decoration: none;
        display: block;
        margin-bottom: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }

    .quick-access-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
    }

    /* Info box */
    .info-box {
        background: linear-gradient(135deg, #2c5282 0%, #2b6cb0 100%);
        color: white;
        padding: 1rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        text-align: center;
        box-shadow: 0 4px 15px rgba(44, 82, 130, 0.3);
    }

    .info-box h4 {
        margin: 0;
        font-size: 0.9rem;
        font-weight: 600;
        opacity: 0.95;
        letter-spacing: 0.5px;
    }

    .info-box p {
        margin: 0.5rem 0 0 0;
        font-size: 1.5rem;
        font-weight: 700;
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# PAGINA PRINCIPAL (Home)
# =============================================================================

def render_header(resumen):
    """Renderiza el encabezado principal."""
    st.markdown(f"""
        <div class="main-header">
            <h1>📊 Sistema de Inteligencia Financiera</h1>
            <p>Análisis Avanzado de la Banca Ecuatoriana | {resumen['anos']} años de datos históricos</p>
        </div>
    """, unsafe_allow_html=True)


def obtener_metadata():
    """Obtiene información sobre la actualización de datos."""
    metadata_path = Path('master_data/metadata.json')
    if metadata_path.exists():
        with open(metadata_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None


def main():
    # Información de actualización
    metadata = obtener_metadata()
    resumen = resumir_metadata(metadata)
    render_header(resumen)

    if not resumen["completa"]:
        st.warning("No se pudo leer completamente la metadata de publicación.")

    # KPIs principales en la parte superior
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="info-box">
            <h4>BANCOS ANALIZADOS</h4>
            <p>{resumen['bancos']}</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="info-box">
            <h4>AÑOS DE HISTORIA</h4>
            <p>{resumen['anos']}</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="info-box">
            <h4>MESES DE DATOS</h4>
            <p>{resumen['meses']}</p>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="info-box">
            <h4>DATOS AL</h4>
            <p>{resumen['datos_al']}</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Introduccion
    st.markdown("""
    ### Bienvenido al Sistema de Inteligencia Financiera

    Esta plataforma permite explorar y analizar el sistema bancario ecuatoriano con datos oficiales
    de la **Superintendencia de Bancos del Ecuador**. Utiliza el menú lateral para navegar entre
    los diferentes módulos de análisis.
    """)

    st.markdown("---")

    # Modulos principales con descripcion detallada
    st.markdown("### 📊 Módulos de Análisis")
    st.markdown("<br>", unsafe_allow_html=True)

    # MODULO 1: PANORAMA
    st.markdown("""
    <div class="card">
        <h3 style="color: #2c5282; margin-bottom: 0.5rem;">📊 1. Panorama del Sistema</h3>
        <p style="color: #4a5568; margin-bottom: 1rem; font-size: 0.95rem;">
            Vista consolidada del sistema bancario ecuatoriano con indicadores clave de mercado y concentración.
        </p>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-top: 1rem;">
            <div>
                <p style="margin: 0; font-weight: 600; color: #1a365d; font-size: 0.9rem;">✓ KPIs del Sistema</p>
                <p style="margin: 0.25rem 0 0 0; color: #718096; font-size: 0.85rem;">Activos totales, cartera, depósitos y liquidez del sistema completo</p>
            </div>
            <div>
                <p style="margin: 0; font-weight: 600; color: #1a365d; font-size: 0.9rem;">✓ Mapa de Mercado</p>
                <p style="margin: 0.25rem 0 0 0; color: #718096; font-size: 0.85rem;">Treemaps jerárquicos interactivos de activos y pasivos con drill-down</p>
            </div>
            <div>
                <p style="margin: 0; font-weight: 600; color: #1a365d; font-size: 0.9rem;">✓ Rankings</p>
                <p style="margin: 0.25rem 0 0 0; color: #718096; font-size: 0.85rem;">Top bancos por activos y pasivos con participación de mercado</p>
            </div>
            <div>
                <p style="margin: 0; font-weight: 600; color: #1a365d; font-size: 0.9rem;">✓ Crecimiento YoY</p>
                <p style="margin: 0.25rem 0 0 0; color: #718096; font-size: 0.85rem;">Variación anual de cartera y depósitos por banco</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # MODULO 2: BALANCE GENERAL
    st.markdown("""
    <div class="card">
        <h3 style="color: #2c5282; margin-bottom: 0.5rem;">⚖️ 2. Balance General</h3>
        <p style="color: #4a5568; margin-bottom: 1rem; font-size: 0.95rem;">
            Análisis temporal detallado del balance con navegación jerárquica de 6 niveles (1→2→4→6 dígitos).
        </p>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-top: 1rem;">
            <div>
                <p style="margin: 0; font-weight: 600; color: #1a365d; font-size: 0.9rem;">✓ Evolución Comparativa</p>
                <p style="margin: 0.25rem 0 0 0; color: #718096; font-size: 0.85rem;">Gráficos de líneas con 3 modos: absoluto, indexado y participación</p>
            </div>
            <div>
                <p style="margin: 0; font-weight: 600; color: #1a365d; font-size: 0.9rem;">✓ Filtros Jerárquicos</p>
                <p style="margin: 0.25rem 0 0 0; color: #718096; font-size: 0.85rem;">Navegación por categoría, grupo, subcuenta y detalle contable</p>
            </div>
            <div>
                <p style="margin: 0; font-weight: 600; color: #1a365d; font-size: 0.9rem;">✓ Heatmap YoY</p>
                <p style="margin: 0.25rem 0 0 0; color: #718096; font-size: 0.85rem;">Matriz banco × mes mostrando crecimiento vs año anterior</p>
            </div>
            <div>
                <p style="margin: 0; font-weight: 600; color: #1a365d; font-size: 0.9rem;">✓ Ranking por Cuenta</p>
                <p style="margin: 0.25rem 0 0 0; color: #718096; font-size: 0.85rem;">Comparación de todos los bancos para un mes específico</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # MODULO 3: PERDIDAS Y GANANCIAS
    st.markdown("""
    <div class="card">
        <h3 style="color: #2c5282; margin-bottom: 0.5rem;">💰 3. Pérdidas y Ganancias</h3>
        <p style="color: #4a5568; margin-bottom: 1rem; font-size: 0.95rem;">
            Análisis de rentabilidad y resultados del estado de pérdidas y ganancias (datos acumulados 12 meses).
        </p>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-top: 1rem;">
            <div>
                <p style="margin: 0; font-weight: 600; color: #1a365d; font-size: 0.9rem;">✓ Evolución Comparativa</p>
                <p style="margin: 0.25rem 0 0 0; color: #718096; font-size: 0.85rem;">Comparación multi-banco de margenes (MNI, MBF, MNF, MDI, MOP, GAI, GDE)</p>
            </div>
            <div>
                <p style="margin: 0; font-weight: 600; color: #1a365d; font-size: 0.9rem;">✓ Modos de Visualización</p>
                <p style="margin: 0.25rem 0 0 0; color: #718096; font-size: 0.85rem;">Valores absolutos (millones USD), indexado (base 100) y participación (%)</p>
            </div>
            <div>
                <p style="margin: 0; font-weight: 600; color: #1a365d; font-size: 0.9rem;">✓ Ranking de Rentabilidad</p>
                <p style="margin: 0.25rem 0 0 0; color: #718096; font-size: 0.85rem;">Clasificación de bancos por indicador y estadísticas del sistema</p>
            </div>
            <div>
                <p style="margin: 0; font-weight: 600; color: #1a365d; font-size: 0.9rem;">✓ Total del Sistema</p>
                <p style="margin: 0.25rem 0 0 0; color: #718096; font-size: 0.85rem;">Opción para incluir agregado total del sistema bancario</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # MODULO 4: CAMEL
    st.markdown("""
    <div class="card">
        <h3 style="color: #2c5282; margin-bottom: 0.5rem;">🎯 4. Indicadores CAMEL</h3>
        <p style="color: #4a5568; margin-bottom: 1rem; font-size: 0.95rem;">
            Metodología regulatoria internacional para evaluación de riesgo bancario en 5 dimensiones.
        </p>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-top: 1rem;">
            <div>
                <p style="margin: 0; font-weight: 600; color: #1a365d; font-size: 0.9rem;">✓ C - Capital</p>
                <p style="margin: 0.25rem 0 0 0; color: #718096; font-size: 0.85rem;">Solvencia y patrimonio técnico sobre activos ponderados</p>
            </div>
            <div>
                <p style="margin: 0; font-weight: 600; color: #1a365d; font-size: 0.9rem;">✓ A - Assets (Activos)</p>
                <p style="margin: 0.25rem 0 0 0; color: #718096; font-size: 0.85rem;">Morosidad total/por tipo, cobertura y participación de cartera</p>
            </div>
            <div>
                <p style="margin: 0; font-weight: 600; color: #1a365d; font-size: 0.9rem;">✓ M - Management</p>
                <p style="margin: 0.25rem 0 0 0; color: #718096; font-size: 0.85rem;">Eficiencia operativa y gestión (gastos vs margen financiero)</p>
            </div>
            <div>
                <p style="margin: 0; font-weight: 600; color: #1a365d; font-size: 0.9rem;">✓ E - Earnings (Rentabilidad)</p>
                <p style="margin: 0.25rem 0 0 0; color: #718096; font-size: 0.85rem;">ROE, ROA, depósitos brecha y spread</p>
            </div>
            <div>
                <p style="margin: 0; font-weight: 600; color: #1a365d; font-size: 0.9rem;">✓ L - Liquidity</p>
                <p style="margin: 0.25rem 0 0 0; color: #718096; font-size: 0.85rem;">Fondos disponibles sobre depósitos a corto plazo</p>
            </div>
            <div>
                <p style="margin: 0; font-weight: 600; color: #1a365d; font-size: 0.9rem;">✓ Visualizaciones</p>
                <p style="margin: 0.25rem 0 0 0; color: #718096; font-size: 0.85rem;">Rankings, evolución temporal y heatmaps mensuales con escalas de colores</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Acceso rapido
    st.markdown("### ⚡ Acceso Rápido a Módulos")
    st.markdown("<br>", unsafe_allow_html=True)

    col_a, col_b, col_c, col_d = st.columns(4)

    with col_a:
        st.page_link("pages/1_Panorama.py", label="📊 Panorama", width="stretch")

    with col_b:
        st.page_link("pages/2_Balance_General.py", label="⚖️ Balance General", width="stretch")

    with col_c:
        st.page_link("pages/3_Pérdidas_y_Ganancias.py", label="💰 Pérdidas y Ganancias", width="stretch")

    with col_d:
        st.page_link("pages/4_CAMEL.py", label="🎯 Indicadores CAMEL", width="stretch")

    st.markdown("---")

    # =========================================================================
    # CROSS-PROMO: RADAR COOPERATIVO
    # =========================================================================

    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #1a4731 0%, #276749 50%, #2f855a 100%);
        border-radius: 16px;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 0 10px 40px rgba(26, 71, 49, 0.3);
        display: flex;
        align-items: center;
        justify-content: space-between;
        flex-wrap: wrap;
        gap: 1rem;
    ">
        <div style="flex: 1; min-width: 280px;">
            <h3 style="color: white; margin: 0 0 0.5rem 0; font-size: 1.4rem;">
                🏦 Conoce también el Radar del Sistema Cooperativo
            </h3>
            <p style="color: rgba(255,255,255,0.85); margin: 0; font-size: 0.95rem;">
                Explora el análisis financiero de las 259 cooperativas de ahorro y crédito del Ecuador:
                Balance General, Pérdidas y Ganancias e Indicadores CAMEL oficiales de la SEPS.
            </p>
        </div>
        <div style="flex-shrink: 0;">
            <a href="https://jp1309-cooperativas.streamlit.app"
               target="_blank"
               style="
                   background: white;
                   color: #1a4731;
                   padding: 0.75rem 1.5rem;
                   border-radius: 10px;
                   text-decoration: none;
                   font-weight: 600;
                   font-size: 0.95rem;
                   display: inline-block;
                   box-shadow: 0 4px 12px rgba(0,0,0,0.15);
               ">
                Visitar Radar Cooperativo →
            </a>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Info de datos
    st.markdown(f"""
    ### 📚 Información del Sistema

    **Fuente de Datos:** Superintendencia de Bancos del Ecuador - Catálogo Único de Cuentas
    **Período Cubierto:** {resumen['periodo']} ({resumen['meses']} meses)
    **Instituciones:** {resumen['bancos']} bancos activos del sistema privado
    **Formato:** Archivos Parquet optimizados ({resumen['registros']} de registros de balance)

    Los datos son actualizados mensualmente y procesados con validaciones de calidad
    para garantizar consultas rápidas y eficientes.
    """)

    # Footer
    st.markdown("---")

    col_f1, col_f2 = st.columns([2, 1])

    with col_f1:
        st.markdown(
            """
            <div style='color: #718096; font-size: 0.85rem;'>
                <p><strong>Tecnologías:</strong> Python 3.8+, Streamlit, Plotly, Pandas, NumPy<br>
                <strong>Fuente de datos:</strong> Superintendencia de Bancos del Ecuador<br>
                <strong>Versión:</strong> 1.0.0</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col_f2:
        st.markdown(
            """
            <div style='text-align: right; color: #718096; font-size: 0.85rem;'>
                <p><strong>Desarrollado por</strong><br>Juan Pablo Erráez T.</p>
            </div>
            """,
            unsafe_allow_html=True
        )


if __name__ == "__main__":
    main()
