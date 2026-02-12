# Radar Bancario Ecuador - Resumen del Proyecto

## Dashboard de Business Intelligence para el Sistema Bancario Ecuatoriano

**Versión**: 4.1.0
**Última actualización**: 12 de febrero de 2026

---

## 📊 Estructura del Dashboard

### 5 Módulos Implementados

```
Inicio.py
pages/
????????? 1_Panorama.py             # ??? Vista general del sistema
????????? 2_Balance_General.py      # ??? Analisis temporal de balance
????????? 3_P??rdidas_y_Ganancias.py # ??? Resultados PYG (evolucion + ranking)
????????? 4_CAMEL.py                # ??? Indicadores CAMEL
```

---

## 📁 Datos Procesados

### Archivos Parquet Generados (Optimizados)

| Archivo | Hoja Excel | Registros | Descripción | Tamaño |
|---------|------------|-----------|-------------|--------|
| `balance.parquet` | BAL | 7,993,228 | Balance General | 18.6 MB |
| `pyg.parquet` | PYG | 740,864 | Pérdidas y Ganancias (desacumulado + 12M) | 9.3 MB |
| `camel.parquet` | CAMEL | 225,617 | 39 Indicadores CAMEL categorizados | 1.5 MB |

**Total**: 29.4 MB de datos estructurados
**Periodo**: Enero 2003 - Enero 2026 (23 años, 277 meses)
**Bancos**: 23 instituciones financieras
**Hojas procesadas**: Solo las 3 hojas esenciales (BAL, PYG, CAMEL)

---

## 🔧 Scripts de Procesamiento

### 0. `config.py`
Configuracion centralizada que calcula automaticamente el periodo objetivo.

**Funcionalidad**:
- Calcula periodo objetivo (mes anterior a la fecha actual)
- Genera nombre de carpeta dinamico (`datos_bancos_{mes}_{ano}`)
- URL del portal de la Superintendencia de Bancos
- Todos los scripts de procesamiento importan sus rutas desde aqui

### 1. `descargar.py`
Descarga automatica de archivos Excel desde la Superintendencia de Bancos via Selenium.

**Funcionalidad**:
- Navega al portal web y descarga ZIPs de cada banco
- Descomprime y organiza archivos Excel
- Cada Excel contiene toda la historia (2003-presente)
- 23 bancos activos

### 2. `procesar_balance.py`
Procesa la hoja BAL (Balance General).

**Funcionalidad**:
- Extrae códigos y valores de balance
- Jerarquía de cuentas (Activo, Pasivo, Patrimonio)
- Genera `balance.parquet`

### 3. `procesar_pyg.py`
Procesa la hoja PYG (Pérdidas y Ganancias).

**Funcionalidad especial**:
- **Desacumulación**: Convierte valores acumulados a mensuales
- **Suma móvil 12M**: Calcula rolling sum para comparabilidad
- Códigos personalizados para cuentas resumen (MNI, MBF, MNF, MDI, MOP, GAI, GDE)
- Genera `pyg.parquet`

### 4. `procesar_camel.py`
Procesa la hoja CAMEL (Indicadores Financieros).

**Funcionalidad**:
- Extrae 39 indicadores categorizados por CAMEL
- Categorías: Capital (C), Assets (A), Management (M), Earnings (E), Liquidity (L)
- Incluye composición de cartera por tipo de crédito
- Genera `camel.parquet`

**Nota**: El script `crear_master.py (eliminado)` fue eliminado. Solo procesamos las 3 hojas esenciales (BAL, PYG, CAMEL).

---

## 📈 Visualizaciones Destacadas

### Módulo 1: Panorama
- Treemap jerárquico con drill-down
- Ranking de bancos por activos
- Gráficos de crecimiento anual (Cartera y Depósitos)

### Módulo 2: Balance General
- **Evolución Comparativa**: Hasta 10 bancos simultáneos
  - Modos: Valores Absolutos, Indexado (Base 100), Participación %
- **Heatmap Temporal**: Crecimiento anual por banco (matriz Año × Banco)
- **Velocidad de Crecimiento**: Tasas trimestrales/anuales con estadísticas

### Módulo 3: Perdidas y Ganancias
- **KPIs del Sistema**: MNI, MOP, GAI, GDE
- **Ranking por Ganancia**: Top bancos con slider
- **Crecimiento Anual**: YoY de GDE y MOP
- **Cascada de Márgenes**: Waterfall de formación del resultado
- **Evolución Temporal**: Comparación multi-banco
- **Distribución**: Pie chart de participación en ganancia

### Módulo 4: Indicadores CAMEL
- **KPIs del Sistema**: Solvencia, Morosidad, Cobertura, ROE, Liquidez
- **Análisis por Indicador**: Ranking de bancos por cualquier indicador CAMEL
- **Composición de Cartera**: Treemap por banco y pie chart del sistema
- **Evolución Temporal**: Comparación multi-banco de indicadores
- **Heatmap Anual**: Evolución histórica de indicadores por banco

---

## 🎨 Convenciones de Diseño

### Paleta de Colores
- **RdYlGn**: Rojo-Amarillo-Verde para crecimiento (-10% a +30%)
- **Blues**: Para rankings y valores absolutos
- **Set2/Pastel1**: Para bancos en gráficos multi-línea
- **Set3**: Para pie charts

### Alturas de Gráficos
- KPIs: Auto
- Gráficos principales: 400-500px
- Dinámicas: `max(400, n_elementos * 20-25)`
- Treemaps: 500px

### Formato de Valores
- **Millones USD**: División por 1000
- **Porcentajes**: Multiplicación por 100
- **Display**: `f"${valor:,.0f}M"` o `f"{valor:.1f}%"`

---

## 📚 Documentación Técnica

### Archivos de Documentación

```
docs/
├── README.md                      # Índice de documentación
├── ESTRUCTURA_EXCEL.md            # Estructura de archivos fuente
├── BI_MASTER_FILES.md             # Especificación de parquets
├── VISUALIZACIONES.md             # Diseño conceptual inicial
├── PROCESAMIENTO_PYG.md           # Lógica de desacumulación
├── VISUALIZACION_CRECIMIENTO.md   # Gráficos de crecimiento
├── MODULO_SERIES_TEMPORALES.md    # Series temporales avanzadas
└── MODULO_RENTABILIDAD.md         # Módulo de PYG
```

---

## 🚀 Uso del Dashboard

### Instalación

```bash
# Clonar repositorio
git clone <repo-url>
cd bancos

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar dashboard
streamlit run Inicio.py
```

### Flujo de Trabajo

**Actualizacion automatica** (recomendado):
```bash
python scripts/actualizar_datos.py
```
Esto ejecuta todo el pipeline: descarga, procesamiento (balance, PyG, CAMEL), verificacion y limpieza.

**Actualizacion manual** (paso a paso):
```bash
python scripts/descargar.py           # Descarga ZIPs del portal
python scripts/procesar_balance.py    # Genera balance.parquet
python scripts/procesar_pyg.py        # Genera pyg.parquet
python scripts/procesar_camel.py      # Genera camel.parquet
```

**GitHub Actions**: Se ejecuta automaticamente los dias 10-15 de cada mes.
El archivo `master_data/update_status.json` registra el ultimo periodo procesado
para evitar descargas duplicadas.

**Dashboard**:
```bash
streamlit run Inicio.py
```

---

## 🔍 Casos de Uso

### 1. Análisis de Concentración
**Módulo**: Panorama
- Visualizar participación de mercado
- Identificar bancos dominantes
- Calcular índice HHI

### 2. Comparación de Rentabilidad
**Módulo**: Rentabilidad (PYG)
- Ranking de ganancia del ejercicio
- Evolución temporal de márgenes
- Cascada de formación del resultado

### 3. Análisis de Tendencias
**Módulo**: Series Temporales
- Evolución comparativa multi-banco
- Heatmap de crecimiento histórico
- Detección de patrones estacionales

### 4. Evaluación CAMEL
**Módulo**: CAMEL
- Análisis por dimensiones regulatorias
- Radar charts comparativos
- Identificación de fortalezas/debilidades

### 5. Benchmarking
**Módulo**: Comparador
- Comparar indicadores entre bancos
- Identificar mejores prácticas
- Análisis de brechas

---

## 🎯 Indicadores Clave

### Balance General
- **Activos Totales** (código: 1)
- **Cartera de Créditos** (código: 14)
- **Depósitos del Público** (código: 21)
- **Patrimonio** (código: 3)
- **Fondos Disponibles** (código: 11)

### Pérdidas y Ganancias
- **MNI**: Margen Neto de Intereses
- **MBF**: Margen Bruto Financiero
- **MNF**: Margen Neto Financiero
- **MDI**: Margen de Intermediación
- **MOP**: Margen Operacional
- **GAI**: Ganancia Antes de Impuestos
- **GDE**: Ganancia del Ejercicio

### Indicadores CAMEL
- **C**: Solvencia, Patrimonio/Activos
- **A**: Morosidad, Cobertura
- **M**: Eficiencia Operativa
- **E**: ROA, ROE
- **L**: Liquidez, Fondos/Depósitos

---

## ⚙️ Características Técnicas

### Optimización
- **Caché de Streamlit**: `@st.cache_data` en todas las funciones
- **Formato Parquet**: Almacenamiento columnar eficiente
- **Procesamiento por lotes**: Scripts separados para cada hoja

### Validación de Datos
- Filtrado de cuentas vacías
- Eliminación de duplicados
- Validación de ecuación contable (A = P + E)
- Métricas de calidad en módulo 0

### Manejo de Datos PYG
- **Desacumulación**: Enero = valor directo, Feb-Dic = actual - anterior
- **Suma móvil 12M**: Permite comparar cualquier mes con cualquier otro
- **Ventaja**: Evita estacionalidad, comparable con diciembre (total anual)

---

## 📊 Estadísticas del Proyecto

### Código
- **5 módulos** de visualización
- **5 scripts** de procesamiento
- **1 utilidad** de carga centralizada
- **~2,500 líneas** de código Python

### Visualizaciones
- **20+ gráficos** interactivos implementados
- **Plotly** para visualizaciones dinámicas
- **Streamlit** para interface web

### Datos
- **23 años** de historia (2003-2026)
- **23 bancos** ecuatorianos activos
- **~9 millones** de registros procesados
- **277 meses** de informacion

---

## 🔮 Próximos Pasos

### Visualizaciones Pendientes
- Descomposición temporal (tendencia + estacionalidad)
- Forecasting simple (proyecciones)
- Small multiples (grillas comparativas)
- Métricas de volatilidad

### Funcionalidades
- Exportación de gráficos a PDF/PNG
- Filtros avanzados por segmento
- Alertas automáticas (anomalías)
- Reportes programados

### Datos Adicionales
- Procesar hojas CARTERA e INDICAD completos
- Integrar datos de FUENTES_USOS
- Agregar datos macroeconómicos

---

## 📞 Información del Proyecto

**Fuente de Datos**: Superintendencia de Bancos del Ecuador
- Web: https://www.superbancos.gob.ec/
- Portal Estadístico: https://www.superbancos.gob.ec/estadisticas/portalestudios/

**Tecnologías**:
- Python 3.11+
- Streamlit 1.30+
- Plotly 5.18+
- Pandas 2.1+

**Licencia**: [Especificar licencia]

---

**Desarrollado por**: Dashboard Radar Bancario Ecuador
**Version actual**: 4.1.0
**Ultima actualizacion**: 12 de febrero de 2026
