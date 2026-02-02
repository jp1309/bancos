# Radar Bancario Ecuador

Dashboard interactivo de Business Intelligence para análisis del sistema bancario ecuatoriano, construido con Streamlit y Python.

**Desarrollado por**: Juan Pablo Erráez T.

## Descripción del Proyecto

Sistema de visualización y análisis de datos financieros del sector bancario ecuatoriano, basado en información pública de la Superintendencia de Bancos del Ecuador. Permite análisis temporal, comparativo y de indicadores CAMEL de las instituciones financieras.

El dashboard cuenta con 4 módulos principales que permiten analizar diferentes aspectos del sistema bancario desde múltiples perspectivas: panorama del sistema, estructura de balance, análisis de resultados y evaluación CAMEL.

## Fuente de Datos

- **Origen**: Superintendencia de Bancos del Ecuador - Catálogo Único de Cuentas
- **Período cubierto**: 2003-2025 (276 meses)
- **Instituciones**: 23 bancos activos (de 24 registrados)
- **Registros**: ~15.9 millones de filas
- **Formato**: Archivos Parquet optimizados

### Estructura de Datos

Archivos en `master_data/`:
- `balance.parquet` - Balance General (Activos, Pasivos, Patrimonio)
- `pyg.parquet` - Estado de Resultados (Ingresos y Gastos)
- `indicadores.parquet` - Indicadores financieros calculados
- `camel.parquet` - Ratios CAMEL

Columnas principales:
- `banco`: Nombre de la institución financiera
- `fecha`: Período (formato YYYY-MM-DD)
- `codigo`: Código contable (1-6 dígitos según nivel jerárquico)
- `cuenta`: Descripción de la cuenta contable
- `valor`: Monto en miles de USD

## Estructura del Proyecto

```
bancos/
├── Inicio.py                      # Página principal (multipage app)
├── pages/                         # Módulos de análisis
│   ├── 1_Panorama.py             # Vista general del sistema
│   ├── 2_Balance_General.py      # Análisis temporal de balance
│   ├── 3_Pérdidas_y_Ganancias.py # Estado de resultados
│   └── 4_CAMEL.py                # Indicadores CAMEL
├── utils/                         # Utilidades compartidas
│   ├── data_loader.py            # Carga y validación de datos
│   └── charts.py                 # Componentes de visualización
├── config/
│   └── indicator_mapping.py      # Mapeo de códigos contables
├── scripts/                       # Scripts de automatización
│   ├── config.py                 # Configuración de descarga
│   ├── actualizar_datos.py       # Script maestro
│   ├── descargar.py              # Scraping de datos
│   ├── procesar_balance.py       # Procesamiento de balance
│   ├── procesar_pyg.py           # Procesamiento de PyG
│   └── procesar_camel.py         # Cálculo de indicadores
├── .github/workflows/             # GitHub Actions
│   └── actualizar-datos.yml      # Workflow de actualización
├── master_data/                   # Datos en formato Parquet
│   ├── balance.parquet           # Balance General (~18 MB)
│   ├── pyg.parquet               # Pérdidas y Ganancias (~10 MB)
│   ├── camel.parquet             # Indicadores CAMEL (~1.6 MB)
│   ├── metadata.json             # Info de última actualización
│   └── update_status.json        # Estado del proceso
├── requirements.txt               # Dependencias de Streamlit
└── requirements-scraping.txt      # Dependencias de scraping
```

## Módulos Implementados

### 0. Inicio (Inicio.py)
**Estado**: ✅ Completado

Página principal del dashboard con diseño elegante y sobrio que proporciona:
- **Resumen ejecutivo**: 4 KPIs principales del sistema (bancos activos, período de datos, registros totales, cobertura temporal)
- **Descripción de módulos**: Tarjetas detalladas explicando cada uno de los 4 módulos con sus funcionalidades principales
- **Navegación clara**: Sistema de grid con checkmarks (✓) mostrando las características de cada módulo
- **Branding**: Footer con créditos de desarrollo

Características de diseño:
- Tema de colores azul elegante (#2c5282, #2b6cb0)
- Layout responsive con CSS Grid
- Sombras y gradientes para profundidad visual
- Tipografía jerárquica clara

### 1. Panorama del Sistema (1_Panorama.py)
**Estado**: ✅ Completado

Vista consolidada del sistema bancario ecuatoriano con indicadores clave de mercado y concentración.

Secciones:
- **KPIs del Sistema**: Activos totales, cartera, depósitos, ROA y liquidez del sistema completo
- **Mapa de Mercado**: Treemaps jerárquicos interactivos para activos y pasivos con drill-down en 2 niveles (banco → cuentas de 2 dígitos)
- **Rankings**: Top bancos por activos y pasivos totales
- **Crecimiento YoY**: Variación anual (%) de cartera y depósitos

Características:
- Selector de fecha mensual
- Colores consistentes por banco
- Visualizaciones interactivas con Plotly

### 2. Balance General (2_Balance_General.py)
**Estado**: ✅ Completado

Análisis profundo de la estructura patrimonial y financiera de las instituciones bancarias.

Secciones:

**1. Evolución Comparativa**
- Gráficos de líneas temporales para análisis de tendencias
- Sistema de filtros jerárquicos de 4 niveles (1→2→4→6 dígitos) con validación automática
- Selector múltiple de bancos (hasta 10)
- Tres modos de visualización:
  - **Absoluto**: Valores en millones USD
  - **Indexado**: Base 100 para comparar crecimiento relativo
  - **Participación**: Porcentaje sobre total del sistema
- Opción de incluir línea del total del sistema
- Selector de rango de fechas personalizable (mes/año inicio y fin)

**2. Heatmap de Variación Año contra Año**
- Matriz banco × mes mostrando crecimiento YoY
- Escala de colores divergente (rojo-blanco-verde) para identificar tendencias
- Cobertura de todos los bancos del sistema
- Selector de cuenta contable y año

**3. Ranking por Banco**
- Comparación de valores para un mes específico
- Gráfico de barras horizontales ordenadas
- KPIs del sistema: total, participación del líder, concentración Top 5
- Colores consistentes por banco

Mejoras implementadas:
- ✅ Filtros jerárquicos de 6 dígitos (2026-01-31)
- ✅ Nombres completos sin truncamiento en selectores (2026-01-30)
- ✅ Reorganización de layout para mejor UX (2026-01-30)
- ✅ Validación automática de jerarquías disponibles

### 3. Pérdidas y Ganancias (3_Perdidas_Ganancias.py)
**Estado**: ✅ Completado

Análisis de resultados y rentabilidad del sistema bancario ecuatoriano basado en estados de resultados acumulados a 12 meses.

Indicadores principales (PyG):
- **MNI**: Margen Neto de Intereses
- **MBF**: Margen Bruto Financiero
- **MNF**: Margen Neto Financiero
- **MDI**: Margen de Intermediación
- **MOP**: Margen Operacional
- **GAI**: Ganancia Antes de Impuestos
- **GDE**: Ganancia del Ejercicio

Secciones:

**1. Evolución Comparativa**
- Comparación temporal de múltiples bancos para indicadores de P&G
- Selector de indicador PyG
- Selector múltiple de bancos (hasta 10, con defaults: Pichincha, Pacífico, Guayaquil, Produbanco)
- Tres modos de visualización:
  - **Absoluto**: Millones USD (12 meses)
  - **Indexado**: Base 100 en primer período
  - **Participación**: % sobre total del sistema
- Opción de incluir total del sistema (modo absoluto)
- Selector de período (mes/año inicio y fin)

**2. Ranking de Bancos por Indicador**
- Gráfico de barras horizontales comparando todos los bancos
- Selector de indicador, mes y año
- Valores en millones USD (acumulado 12 meses)
- KPIs: Total sistema, participación #1, concentración Top 5
- Altura dinámica basada en número de bancos

Características técnicas:
- Valores acumulados a 12 meses (`valor_12m`)
- Filtrado automático de valores nulos
- Último día del mes para coincidir con formato de datos
- Hovertemplate personalizado para tooltips informativos

### 4. Indicadores CAMEL (4_CAMEL.py)
**Estado**: ✅ Completado

Dashboard de evaluación bancaria según metodología CAMEL (Capital, Assets, Management, Earnings, Liquidity).

Dimensiones implementadas:

**C - Capital**
- Solvencia (Patrimonio técnico / Activos ponderados)
- Patrimonio / Activos totales
- Apalancamiento

**A - Calidad de Activos**
- Morosidad (Total, Comercial, Consumo, Vivienda, Microempresa)
- Cobertura de cartera problemática
- Cartera improductiva / Total cartera

**M - Gestión (Management)**
- Eficiencia operativa (Gastos operacionales / Margen financiero)
- Gastos de personal / Activo productivo
- Absorción del margen financiero

**E - Rentabilidad (Earnings)**
- ROE (Resultados / Patrimonio promedio)
- ROA (Resultados / Activo promedio)
- Margen de intermediación financiera
- Rentabilidad operacional sobre activos

**L - Liquidez**
- Fondos disponibles / Total depósitos corto plazo
- Cobertura de 25 mayores depositantes
- Activos líquidos / Pasivos corto plazo

Secciones:

**1. Análisis por Indicador**
- Selector de dimensión CAMEL (C, A, M, E, L)
- Dropdown de indicadores específicos por dimensión
- Selector de fecha mensual
- Visualizaciones:
  - **Ranking**: Gráfico de barras horizontales con todos los bancos
  - **Tabla completa**: Datos tabulares ordenados con formato
- Estadísticas del sistema: promedio, mediana, rango
- Colores por dimensión para identificación visual

**2. Evolución Temporal**
- Análisis de tendencias de indicadores CAMEL
- Selector de dimensión e indicador
- Selector múltiple de bancos (hasta 8)
- Rango de fechas personalizable (por defecto desde Enero 2015)
- Gráfico de líneas con colores consistentes por banco

**3. Heatmap Mensual**
- Matriz banco × mes para identificar patrones temporales
- Selector de dimensión, indicador y año
- Escala de colores automática (azul-blanco-rojo)
- Todos los bancos del sistema en un solo vistazo

Características técnicas:
- Códigos de indicadores actualizados y validados
- Manejo de Management con códigos GO_*, GP_*, AP_PC
- Filtrado automático de valores nulos
- Formato de tooltips personalizado
- Altura dinámica de gráficos según número de bancos

## Jerarquía de Cuentas Contables

Sistema de códigos del Catálogo Único de Cuentas:

```
Nivel 1 (1 dígito):  1 = Activos
                     2 = Pasivos
                     3 = Patrimonio
                     6, 7 = Cuentas de orden

Nivel 2 (2 dígitos): 11 = Fondos Disponibles
                     14 = Cartera de Créditos
                     21 = Obligaciones con el Público
                     ...

Nivel 3 (4 dígitos): 1401 = Cartera Comercial
                     1402 = Cartera de Consumo
                     1403 = Cartera de Vivienda
                     ...

Nivel 4 (6 dígitos): Detalle específico de subcuentas
```

## Indicadores CAMEL

Metodología de evaluación bancaria implementada:

- **C (Capital)**: Solvencia, Patrimonio técnico/Activos ponderados
- **A (Assets)**: Morosidad total/por tipo, Cobertura de cartera
- **M (Management)**: Eficiencia operativa, Gastos/Margen financiero
- **E (Earnings)**: ROE, ROA, Margen de intermediación
- **L (Liquidity)**: Fondos disponibles/Depósitos, Cobertura depositantes

## Instalación y Uso

### Requisitos
- Python 3.8+
- Streamlit 1.28+
- Pandas, NumPy, Plotly

### Instalación

```bash
cd bancos
pip install streamlit pandas plotly pyarrow
```

### Ejecución

```bash
streamlit run Inicio.py --server.port 8502
```

Acceder en: http://localhost:8502

## Actualización Automática de Datos

El sistema incluye un proceso automatizado que actualiza los datos mensualmente usando GitHub Actions.

### Funcionamiento

- **Cuándo:** Del día 10 al 15 de cada mes a las 8:00 AM (hora Ecuador)
- **Qué hace:** Descarga los datos del mes anterior desde la Superintendencia de Bancos
- **Proceso:**
  1. Descarga archivos ZIP de cada banco
  2. Extrae y procesa hojas Excel (Balance, PyG)
  3. Calcula indicadores CAMEL
  4. Genera archivos `.parquet` optimizados
  5. Hace commit automático a GitHub
  6. Streamlit Cloud se actualiza automáticamente

### Archivos del Sistema de Automatización

```
.github/workflows/
└── actualizar-datos.yml    # Workflow de GitHub Actions

scripts/
├── config.py               # Configuración del periodo a descargar
├── actualizar_datos.py     # Script maestro de orquestación
├── descargar.py            # Scraping de la Superintendencia
├── procesar_balance.py     # Procesa Balance General
├── procesar_pyg.py         # Procesa Pérdidas y Ganancias
└── procesar_camel.py       # Calcula indicadores CAMEL
```

### Ejecución Manual

Desde GitHub Actions:
1. Ir a https://github.com/jp1309/bancos/actions
2. Seleccionar "Actualizar Datos Bancarios"
3. Clic en "Run workflow"

Desde línea de comandos:
```bash
python scripts/actualizar_datos.py
```

### Documentación Detallada

Ver [docs/AUTOMATIZACION.md](docs/AUTOMATIZACION.md) para información completa sobre el sistema de actualización.

## Calidad de Datos

### Problemas Conocidos
- Banco Amazonas: No tiene datos (1 de 24 bancos faltante)
- 11.7% de indicadores vacíos (448K registros sin cuenta)
- 32.67% de valores nulos en INDICAD
- Duplicados en PYG: 160K registros
- Cobertura histórica variable (2003-2008: solo 17 bancos)

### Validaciones Implementadas
- Filtro de cuentas vacías en carga
- Deduplicación por banco+fecha+código
- Métricas de calidad registradas
- Cache de datos con Streamlit

## Funcionalidades Futuras

### Módulos en Planificación

**0. Calidad de Datos**
- Dashboard de métricas de completitud
- Heatmap de cobertura temporal por banco y período
- Alertas de indicadores con >20% valores nulos
- Validación de ecuación contable (Activos = Pasivos + Patrimonio)

**5. Perfil Individual de Banco**
- Selector de banco único
- Resumen ejecutivo con KPIs principales
- Gráfico radar CAMEL del banco seleccionado
- Estructura de balance (gráfico de barras apiladas 100%)
- Evolución histórica de indicadores clave (últimos 24 meses)
- Comparación con promedio del sistema

**Mejoras Adicionales**
- Exportación de datos y gráficos a Excel/PDF
- Gráfico radar para comparación multibanco
- Matriz de correlación entre indicadores
- Alertas automáticas de eventos significativos
- Análisis predictivo de tendencias

## Estado Actual del Proyecto

### Completado ✅
1. ✅ Arquitectura multipage de Streamlit con 5 páginas
2. ✅ Página principal (Inicio) con diseño elegante y descripción de módulos
3. ✅ Carga optimizada de datos con cache y validación
4. ✅ **Módulo 1: Panorama del Sistema** con KPIs, treemaps, rankings y YoY
5. ✅ **Módulo 2: Balance General** con 3 secciones (Evolución, Heatmap, Ranking)
6. ✅ **Módulo 3: Pérdidas y Ganancias** con análisis de resultados acumulados
7. ✅ **Módulo 4: Indicadores CAMEL** con 5 dimensiones y 3 tipos de visualización
8. ✅ Filtros jerárquicos de 6 niveles con validación automática
9. ✅ Sistema de colores consistente por banco
10. ✅ Mapeo robusto de códigos contables e indicadores
11. ✅ Múltiples modos de visualización (Absoluto, Indexado, Participación)

### En Desarrollo ⏳
- Módulo de Calidad de Datos (transparencia sobre cobertura y completitud)
- Módulo de Perfil Individual por Banco
- Exportación de reportes a Excel/PDF
- Análisis predictivo y alertas automáticas

## Decisiones Técnicas

### Arquitectura
- **Multipage Streamlit**: Separación modular de funcionalidades
- **Cache de datos**: `@st.cache_data` para optimizar carga
- **Parquet**: Formato eficiente para grandes volúmenes

### Validación Robusta
- Códigos contables fijos (no búsquedas por texto)
- Validación de jerarquías antes de mostrar
- Manejo de casos edge (cuentas sin subcuentas, bancos sin datos)

### UX/UI
- Filtros contextuales (solo opciones válidas)
- Labels descriptivos sin truncamiento
- Tooltips informativos en gráficos
- Colores accesibles y distinguibles

## Próximos Pasos

1. **Mejoras de Calidad**:
   - Implementar módulo de Calidad de Datos con métricas de completitud
   - Agregar tests unitarios para funciones de carga y validación
   - Documentar estructura de códigos contables

2. **Funcionalidades Adicionales**:
   - Módulo de Perfil Individual por Banco
   - Exportación de gráficos y datos a Excel/PDF
   - Comparador avanzado con gráfico radar multibanco

3. **Optimización**:
   - Implementar cache más granular por módulo
   - Optimizar queries para reducir tiempo de carga
   - Mejorar responsividad en dispositivos móviles

## Tecnologías Utilizadas

- **Python 3.8+**: Lenguaje principal
- **Streamlit 1.28+**: Framework de dashboard interactivo
- **Pandas**: Manipulación y análisis de datos
- **Plotly**: Visualizaciones interactivas
- **PyArrow**: Lectura eficiente de archivos Parquet
- **NumPy**: Operaciones numéricas

## Licencia

Este proyecto utiliza datos públicos de la Superintendencia de Bancos del Ecuador.

## Autor

**Juan Pablo Erráez T.**

Desarrollado con asistencia de Claude AI (Anthropic).

## Historial de Cambios

- **2026-02-01**:
  - Rediseño completo de página Inicio con diseño elegante
  - Actualización de tema de colores a azul profesional
  - Documentación completa para GitHub
  - Actualización de README con todos los módulos implementados

- **2026-01-31**:
  - Corrección de indicadores de Management en CAMEL (códigos GO_*, GP_*, AP_PC)
  - Implementación completa de módulo CAMEL con 3 secciones
  - Implementación de filtros de 6 dígitos en Balance General

- **2026-01-30**:
  - Corrección de truncamiento en nombres de cuentas
  - Reorganización de layout (selector de bancos en fila separada)
  - Mejoras en UX de filtros jerárquicos

---

**Nota**: Este README refleja el estado del proyecto al 2026-02-01. Para información detallada sobre el uso de cada módulo, consulte la página de Inicio del dashboard.
