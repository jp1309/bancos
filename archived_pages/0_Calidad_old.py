# -*- coding: utf-8 -*-
"""
Modulo 0: Calidad de Datos
Dashboard de validacion y transparencia sobre la calidad de los datos.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import sys

# Agregar path para imports
sys.path.append(str(Path(__file__).parent.parent))

from utils.data_loader import cargar_balance, cargar_pyg, cargar_camel, obtener_fechas_disponibles
from utils.data_quality import (
    calcular_completitud_general,
    validar_cobertura_bancos,
    calcular_cobertura_por_fecha,
    detectar_bancos_faltantes,
    detectar_fechas_faltantes,
    analizar_nulos_por_indicador,
    validar_ecuacion_contable,
    generar_resumen_calidad,
    exportar_reporte_calidad,
)
from config.indicator_mapping import BANCOS_SISTEMA

# =============================================================================
# CONFIGURACION DE PAGINA
# =============================================================================

st.set_page_config(
    page_title="Calidad de Datos | Radar Bancario",
    page_icon="🔍",
    layout="wide",
)

# =============================================================================
# ESTILOS
# =============================================================================

st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%);
        border-radius: 12px;
        padding: 1.2rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border-left: 4px solid #3182ce;
        margin-bottom: 1rem;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #1a365d;
    }
    .metric-label {
        font-size: 0.85rem;
        color: #718096;
        text-transform: uppercase;
    }
    .alert-card {
        background: #fff5f5;
        border-left: 4px solid #e53e3e;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 0.5rem;
    }
    .success-card {
        background: #f0fff4;
        border-left: 4px solid #38a169;
        padding: 1rem;
        border-radius: 8px;
    }
    .warning-card {
        background: #fffaf0;
        border-left: 4px solid #dd6b20;
        padding: 1rem;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)


# =============================================================================
# FUNCIONES DE RENDERIZADO
# =============================================================================

def render_metric_card(valor, label, color="#3182ce"):
    st.markdown(f"""
        <div class="metric-card" style="border-left-color: {color};">
            <div class="metric-value">{valor}</div>
            <div class="metric-label">{label}</div>
        </div>
    """, unsafe_allow_html=True)


def render_estado_badge(estado):
    colores = {
        'OK': ('🟢', '#38a169', 'success-card'),
        'ADVERTENCIA': ('🟡', '#dd6b20', 'warning-card'),
        'REVISAR': ('🔴', '#e53e3e', 'alert-card'),
        'ERROR': ('🔴', '#e53e3e', 'alert-card'),
    }
    emoji, color, clase = colores.get(estado, ('⚪', '#718096', 'metric-card'))
    return f'<div class="{clase}"><strong>{emoji} Estado General: {estado}</strong></div>'


# =============================================================================
# PAGINA PRINCIPAL
# =============================================================================

def main():
    st.title("🔍 Calidad de Datos")
    st.markdown("Validacion y transparencia sobre los datos antes del analisis.")
    st.markdown("---")

    # Cargar los 3 datasets esenciales
    with st.spinner("Cargando y validando datos..."):
        datos = {
            'dataframes': {},
            'calidad': {},
            'errores': []
        }

        try:
            df_balance, cal_balance = cargar_balance()
            datos['dataframes']['balance'] = df_balance
            datos['calidad']['balance'] = cal_balance
        except Exception as e:
            datos['errores'].append(f"balance: {str(e)}")

        try:
            df_pyg, cal_pyg = cargar_pyg()
            datos['dataframes']['pyg'] = df_pyg
            datos['calidad']['pyg'] = cal_pyg
        except Exception as e:
            datos['errores'].append(f"pyg: {str(e)}")

        try:
            df_camel, cal_camel = cargar_camel()
            datos['dataframes']['camel'] = df_camel
            datos['calidad']['camel'] = cal_camel
        except Exception as e:
            datos['errores'].append(f"camel: {str(e)}")

    if datos.get('errores'):
        for error in datos['errores']:
            st.warning(f"Advertencia: {error}")

    if not datos['dataframes']:
        st.error("No se pudieron cargar los datos.")
        st.info("Asegurate de haber ejecutado los scripts de procesamiento (procesar_balance.py, procesar_pyg.py, procesar_camel.py)")
        return

    # Generar resumen de calidad
    resumen = generar_resumen_calidad(datos)

    # ==========================================================================
    # SECCION 1: RESUMEN EJECUTIVO
    # ==========================================================================

    st.subheader("Resumen Ejecutivo")

    # Estado general
    st.markdown(render_estado_badge(resumen['estado_general']), unsafe_allow_html=True)

    # KPIs principales
    col1, col2, col3, col4 = st.columns(4)

    completitud = resumen['metricas'].get('completitud', {})
    cal_balance = datos['calidad'].get('balance', {})
    cal_camel = datos['calidad'].get('camel', {})

    with col1:
        pct = completitud.get('pct_completitud', 0)
        color = '#38a169' if pct > 95 else '#dd6b20' if pct > 85 else '#e53e3e'
        render_metric_card(f"{pct}%", "Completitud de Datos", color)

    with col2:
        bancos = cal_balance.get('bancos', 0)
        esperados = len(BANCOS_SISTEMA)
        color = '#38a169' if bancos >= esperados else '#dd6b20'
        render_metric_card(f"{bancos}/{esperados}", "Bancos Activos", color)

    with col3:
        render_metric_card(
            f"{cal_balance.get('fechas', 0)}",
            "Meses de Datos",
            "#3182ce"
        )

    with col4:
        alertas = len(resumen.get('alertas', []))
        color = '#38a169' if alertas == 0 else '#dd6b20' if alertas < 3 else '#e53e3e'
        render_metric_card(f"{alertas}", "Alertas Activas", color)

    # ==========================================================================
    # SECCION 2: ALERTAS
    # ==========================================================================

    if resumen.get('alertas'):
        st.subheader("Alertas")
        for alerta in resumen['alertas']:
            st.markdown(f'<div class="alert-card">⚠️ {alerta}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="success-card">✅ No hay alertas. Los datos estan en buen estado.</div>', unsafe_allow_html=True)

    st.markdown("---")

    # ==========================================================================
    # SECCION 3: COBERTURA TEMPORAL (Heatmap)
    # ==========================================================================

    st.subheader("Cobertura de Bancos por Ano")

    if 'balance' in datos['dataframes']:
        df_balance = datos['dataframes']['balance']

        # Crear heatmap de cobertura
        cobertura = validar_cobertura_bancos(df_balance)

        # Limitar a ultimos 10 anos para legibilidad
        anos_recientes = sorted(cobertura.columns)[-15:]
        cobertura_reciente = cobertura[anos_recientes]

        fig_heatmap = px.imshow(
            cobertura_reciente,
            labels=dict(x="Ano", y="Banco", color="Tiene datos"),
            color_continuous_scale=[[0, '#fed7d7'], [1, '#c6f6d5']],
            aspect='auto'
        )
        fig_heatmap.update_layout(
            height=600,
            margin=dict(l=10, r=10, t=30, b=10),
        )
        fig_heatmap.update_coloraxes(showscale=False)

        st.plotly_chart(fig_heatmap, use_container_width=True)

        # Mostrar bancos faltantes
        bancos_faltantes = detectar_bancos_faltantes(df_balance)
        if bancos_faltantes:
            st.warning(f"**Bancos no encontrados en los datos:** {', '.join(bancos_faltantes)}")

        # Estadisticas de cobertura
        cobertura_por_fecha = calcular_cobertura_por_fecha(df_balance)

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Cobertura por ano (promedio de bancos)**")
            cob_anual = cobertura_por_fecha.groupby('ano')['bancos_con_datos'].mean().round(1)
            fig_bar = px.bar(
                x=cob_anual.index,
                y=cob_anual.values,
                labels={'x': 'Ano', 'y': 'Bancos promedio'},
            )
            fig_bar.update_traces(marker_color='#3182ce')
            fig_bar.update_layout(height=300, margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig_bar, use_container_width=True)

        with col2:
            # Fechas con menos bancos
            st.markdown("**Meses con menor cobertura**")
            peor_cobertura = cobertura_por_fecha.nsmallest(10, 'bancos_con_datos')
            peor_cobertura['fecha_str'] = peor_cobertura['fecha'].dt.strftime('%Y-%m')
            st.dataframe(
                peor_cobertura[['fecha_str', 'bancos_con_datos']].rename(
                    columns={'fecha_str': 'Fecha', 'bancos_con_datos': 'Bancos'}
                ),
                hide_index=True,
                use_container_width=True
            )

    st.markdown("---")

    # ==========================================================================
    # SECCION 4: VALIDACION DE DATOS CAMEL
    # ==========================================================================

    st.subheader("Calidad de Datos - Indicadores CAMEL")

    if 'camel' in datos['dataframes']:
        df_camel = datos['dataframes']['camel']
        cal_camel = datos['calidad'].get('camel', {})

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Indicadores Unicos", cal_camel.get('indicadores_unicos', 'N/A'))
        with col2:
            st.metric("Registros Procesados", f"{cal_camel.get('registros_limpios', 0):,}")
        with col3:
            categorias = len(cal_camel.get('categorias', []))
            st.metric("Categorias CAMEL", categorias)

        # Mostrar categorias
        if cal_camel.get('categorias'):
            st.markdown("**Categorias procesadas**: " + ", ".join(cal_camel['categorias']))
    else:
        st.warning("Datos CAMEL no disponibles")

    st.markdown("---")

    # ==========================================================================
    # SECCION 5: VALIDACION CONTABLE (A = P + E)
    # ==========================================================================

    st.subheader("Validacion de Ecuacion Contable")
    st.markdown("Verifica que **Activo = Pasivo + Patrimonio** para cada banco.")

    if 'balance' in datos['dataframes']:
        df_balance = datos['dataframes']['balance']

        # Selector de fecha
        fechas = obtener_fechas_disponibles(df_balance)
        fecha_validar = st.selectbox(
            "Selecciona fecha a validar",
            options=fechas[:24],  # Ultimos 2 anos
            format_func=lambda x: x.strftime('%B %Y'),
            index=0
        )

        validacion = validar_ecuacion_contable(df_balance, fecha=fecha_validar)

        # Resumen de validacion
        total_bancos = len(validacion)
        bancos_ok = len(validacion[validacion['estado'] == 'OK'])
        bancos_warn = len(validacion[validacion['estado'] == 'Advertencia'])
        bancos_error = len(validacion[validacion['estado'] == 'Error'])

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Bancos OK", bancos_ok, delta=None)
        with col2:
            st.metric("Advertencias", bancos_warn, delta=None)
        with col3:
            st.metric("Errores", bancos_error, delta=None)

        # Tabla de validacion
        validacion_display = validacion.copy()
        validacion_display['activo'] = validacion_display['activo'].apply(lambda x: f"${x/1000:,.0f}M")
        validacion_display['pasivo_patrimonio'] = validacion_display['pasivo_patrimonio'].apply(lambda x: f"${x/1000:,.0f}M")
        validacion_display['diferencia'] = validacion_display['diferencia'].apply(lambda x: f"${x/1000:,.2f}M")

        # Colorear por estado
        def highlight_estado(row):
            if row['estado'] == 'OK':
                return ['background-color: #c6f6d5'] * len(row)
            elif row['estado'] == 'Advertencia':
                return ['background-color: #fefcbf'] * len(row)
            else:
                return ['background-color: #fed7d7'] * len(row)

        st.dataframe(
            validacion_display[['banco', 'activo', 'pasivo_patrimonio', 'diferencia', 'pct_diferencia', 'estado']].style.apply(
                highlight_estado, axis=1
            ),
            hide_index=True,
            use_container_width=True
        )

    st.markdown("---")

    # ==========================================================================
    # SECCION 6: EXPORTAR REPORTE
    # ==========================================================================

    st.subheader("Exportar Reporte de Calidad")

    col1, col2 = st.columns([1, 3])

    with col1:
        if st.button("📥 Generar Reporte Excel", type="primary"):
            with st.spinner("Generando reporte..."):
                excel_buffer = exportar_reporte_calidad(datos)
                st.download_button(
                    label="⬇️ Descargar Reporte",
                    data=excel_buffer,
                    file_name="reporte_calidad_datos.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

    with col2:
        st.markdown("""
        El reporte incluye:
        - Resumen ejecutivo de calidad
        - Lista de alertas activas
        - Matriz de cobertura bancos x anos
        - Indicadores con valores nulos
        - Validacion contable por banco
        """)


if __name__ == "__main__":
    main()
