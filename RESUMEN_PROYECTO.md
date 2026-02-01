# Radar Bancario Ecuador - Resumen del Proyecto

## Dashboard de Business Intelligence para el Sistema Bancario Ecuatoriano

**Versión**: 4.0.0
**Última actualización**: 26 de enero de 2026

---

## 📊 Estructura del Dashboard

### 5 Módulos Implementados

```
pages/
├── 0_Calidad.py              # ✅ Validación de calidad de datos
├── 1_Panorama.py             # ✅ Vista general del sistema
├── 2_Balance_General.py      # ✅ Análisis temporal de balance (3 viz)
├── 3_Perdidas_Ganancias.py   # ✅ Rentabilidad y resultados (6 viz)
└── 4_CAMEL.py                # ✅ Indicadores CAMEL (5 viz)
```

---

## 📁 Datos Procesados

### Archivos Parquet Generados (Optimizados)

| Archivo | Hoja Excel | Registros | Descripción | Tamaño |
|---------|------------|-----------|-------------|--------|
| `balance.parquet` | BAL | 8,300,000+ | Balance General | 18 MB |
| `pyg.parquet` | PYG | 769,792 | Pérdidas y Ganancias (desacumulado + 12M) | 9.5 MB |
| `camel.parquet` | CAMEL | 233,680 | 39 Indicadores CAMEL categorizados | 1.6 MB |

**Total**: 29.1 MB de datos estructurados (reducción del 22% vs versión anterior)
**Periodo**: Enero 2003 - Diciembre 2025 (23 años, 276 meses)
**Bancos**: 24 instituciones financieras
**Hojas procesadas**: Solo las 3 hojas esenciales (BAL, PYG, CAMEL)

---

## 🔧 Scripts de Procesamiento

### 1. `descargar.py`
Descarga automática de archivos Excel desde la Superintendencia de Bancos.

**Funcionalidad**:
- Descarga mensual de enero 2003 a diciembre 2025
- Organización por año/mes
- Detección de duplicados
- 276 archivos históricos

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

**Nota**: El script `crear_master.py` fue eliminado. Solo procesamos las 3 hojas esenciales (BAL, PYG, CAMEL).

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
streamlit run app.py
```

### Flujo de Trabajo

1. **Descarga de datos**:
   ```bash
   python descargar.py
   ```

2. **Procesamiento**:
   ```bash
   python procesar_balance.py
   python procesar_pyg.py
   python crear_master.py  # Para otros archivos
   ```

3. **Dashboard**:
   ```bash
   streamlit run app.py
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
- **23 años** de historia (2003-2025)
- **24 bancos** ecuatorianos
- **13+ millones** de registros procesados
- **276 meses** de información

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
**Versión actual**: 4.0.0
**Última actualización**: 26 de enero de 2026
