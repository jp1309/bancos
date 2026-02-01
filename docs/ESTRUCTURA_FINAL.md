# Estructura Final del Dashboard - Radar Bancario Ecuador

**Versión**: 4.0.0
**Fecha**: 26 de enero de 2026
**Estado**: ✅ Implementado y Documentado

---

## Resumen Ejecutivo

El dashboard de Business Intelligence para el sistema bancario ecuatoriano ha sido reestructurado para enfocarse en los análisis más críticos y relevantes. La versión 4.0.0 consolida 4 módulos principales que cubren:

1. **Validación de Datos** - Calidad y cobertura
2. **Vista General** - Panorama del sistema
3. **Análisis de Balance** - Evolución temporal de activos y pasivos
4. **Análisis de Resultados** - Rentabilidad y pérdidas/ganancias

---

## Arquitectura del Dashboard

### Estructura de Archivos

```
bancos/
├── app.py                          # Punto de entrada principal
├── pages/                          # Módulos del dashboard
│   ├── 0_Calidad.py               # Validación de calidad de datos
│   ├── 1_Panorama.py              # Vista general del sistema
│   ├── 2_Balance_General.py       # Análisis temporal de balance
│   └── 3_Perdidas_Ganancias.py    # Rentabilidad y resultados
├── utils/                          # Utilidades compartidas
│   ├── data_loader.py             # Carga centralizada de datos
│   ├── data_quality.py            # Funciones de validación
│   └── charts.py                  # Componentes gráficos
├── config/                         # Configuración
│   └── indicator_mapping.py       # Mapeo de códigos contables
├── master_data/                    # Datos procesados (Parquet)
│   ├── balance.parquet            # Balance General
│   ├── pyg.parquet                # Pérdidas y Ganancias
│   ├── indicadores.parquet        # Indicadores financieros
│   ├── cartera.parquet            # Estructura de cartera
│   └── fuentes_usos.parquet       # Fuentes y usos
├── docs/                           # Documentación técnica
└── scripts de procesamiento/       # Scripts ETL
    ├── descargar.py
    ├── procesar_balance.py
    ├── procesar_pyg.py
    └── crear_master.py
```

---

## Módulos Implementados

### Módulo 0: Calidad de Datos

**Archivo**: `pages/0_Calidad.py`
**Ícono**: 🔍
**Propósito**: Validar la calidad y cobertura de los datos antes del análisis

**Contenido**:
- KPIs de completitud y cobertura
- Heatmap de disponibilidad temporal por banco
- Lista de indicadores con valores nulos
- Validación de ecuación contable (A = P + E)
- Reporte de calidad descargable

**Métricas Principales**:
- % de completitud de datos
- Bancos activos vs total
- Rango de fechas disponibles
- Alertas de calidad

---

### Módulo 1: Panorama del Sistema

**Archivo**: `pages/1_Panorama.py`
**Ícono**: 🏦
**Propósito**: Vista general del sistema bancario ecuatoriano

**Visualizaciones**:
1. **KPIs del Sistema**
   - Total Activos
   - Total Cartera de Créditos
   - Total Depósitos
   - Total Patrimonio

2. **Treemap Jerárquico**
   - Composición de activos con drill-down
   - Jerarquía: Banco → Categoría

3. **Ranking de Bancos**
   - Barras horizontales por activos totales
   - Ordenado de mayor a menor

4. **Crecimiento Anual**
   - Barras horizontales de variación YoY
   - Escala de colores RdYlGn
   - Aplicado a Cartera y Depósitos

**Filtros**:
- Selector de fecha (mes/año)
- Comparación automática vs año anterior

---

### Módulo 2: Balance General

**Archivo**: `pages/2_Balance_General.py`
**Ícono**: 📊
**Propósito**: Análisis temporal de las cuentas de balance

**Visualizaciones**:

#### 2.1 Evolución Comparativa
- **Tipo**: Gráfico de líneas múltiples
- **Bancos**: Hasta 10 seleccionables
- **Modos**:
  - Valores Absolutos (millones USD)
  - Indexado (Base 100)
  - Participación % del sistema
- **Opción**: Incluir Total Sistema
- **Cuentas disponibles**: Todos los códigos de balance

#### 2.2 Heatmap Temporal
- **Tipo**: Matriz de calor Año × Banco
- **Métrica**: Crecimiento anual (%)
- **Ordenamiento**: Por valor absoluto (bancos más grandes arriba)
- **Escala**: RdYlGn centrada en 0
- **Selección**: Por banco o sistema completo

#### 2.3 Velocidad de Crecimiento
- **Tipo**: Barras por período
- **Períodos**: Trimestral o Anual
- **Estadísticas**:
  - Promedio de crecimiento
  - Crecimiento máximo
  - Crecimiento mínimo
  - Volatilidad (desviación estándar)

**Filtros**:
- Selector de cuenta de balance
- Multiselect de bancos
- Modo de visualización
- Período de análisis

**Fuente de Datos**: `master_data/balance.parquet`

---

### Módulo 3: Perdidas y Ganancias

**Archivo**: `pages/3_Perdidas_Ganancias.py`
**Ícono**: 💰
**Propósito**: Análisis de rentabilidad y resultados del sistema

**Indicadores PYG**:
- **MNI**: Margen Neto de Intereses
- **MBF**: Margen Bruto Financiero
- **MNF**: Margen Neto Financiero
- **MDI**: Margen de Intermediación
- **MOP**: Margen Operacional
- **GAI**: Ganancia Antes de Impuestos
- **GDE**: Ganancia del Ejercicio

**Visualizaciones**:

#### 3.1 KPIs del Sistema
- 4 métricas principales en cards
- Suma de todos los bancos
- Valores en millones USD
- Suma móvil 12 meses

#### 3.2 Ranking de Rentabilidad
- Barras horizontales por Ganancia del Ejercicio
- Slider para Top N bancos (5 a 24)
- Ordenado de mayor a menor
- Escala de color azul por intensidad

#### 3.3 Crecimiento Anual
- 2 gráficos: GDE y MOP
- Barras horizontales con variación YoY
- Escala RdYlGn (-50% a +50%)
- Línea de referencia en 0%

#### 3.4 Cascada de Márgenes
- Gráfico waterfall de formación del resultado
- Selector de banco
- 7 etapas: MNI → MBF → MNF → MDI → MOP → GAI → GDE
- Valores en millones USD

#### 3.5 Evolución Temporal
- Líneas múltiples comparativas
- Hasta 8 bancos seleccionables
- Selector de indicador PYG
- Hover unificado por fecha
- Suma móvil 12 meses

#### 3.6 Distribución de Rentabilidad
- Pie chart con participación por banco
- Top 10 bancos + categoría "Otros"
- Solo valores positivos (ganancias)
- Porcentajes y valores absolutos

**Filtros**:
- Selector de fecha
- Selector de banco (para cascada)
- Multiselect de bancos (para evolución)
- Selector de indicador PYG
- Slider para Top N

**Fuente de Datos**: `master_data/pyg.parquet`

**Nota Técnica**: Los datos de PYG usan `valor_12m` (suma móvil de 12 meses) para permitir comparabilidad entre cualquier mes del año, evitando problemas de estacionalidad.

---

## Datos Procesados

### Balance General (`balance.parquet`)
- **Registros**: 8,300,000+
- **Tamaño**: ~80 MB
- **Columnas**: banco, fecha, codigo, cuenta, valor
- **Fuente**: Hoja BAL de archivos Excel

### Pérdidas y Ganancias (`pyg.parquet`)
- **Registros**: 769,792
- **Tamaño**: ~9.4 MB
- **Columnas**: banco, fecha, codigo, cuenta, valor_acumulado, valor_mes, valor_12m
- **Fuente**: Hoja PYG de archivos Excel
- **Procesamiento especial**: Desacumulación + Suma móvil 12M

### Indicadores (`indicadores.parquet`)
- **Registros**: 3,800,000+
- **Tamaño**: ~45 MB
- **Fuente**: Hoja INDICAD

### Cartera (`cartera.parquet`)
- **Registros**: 500,000+
- **Tamaño**: ~8 MB
- **Fuente**: Hoja CARTERA

### Fuentes y Usos (`fuentes_usos.parquet`)
- **Registros**: 400,000+
- **Tamaño**: ~6 MB
- **Fuente**: Hoja FUENTES_USOS

**Total**: ~150 MB de datos estructurados
**Periodo**: Enero 2003 - Diciembre 2025 (23 años, 276 meses)
**Bancos**: 24 instituciones financieras

---

## Convenciones de Diseño

### Paleta de Colores
- **RdYlGn**: Rojo-Amarillo-Verde para crecimiento
  - Rojo: Valores negativos (decrecimiento)
  - Amarillo: Valores neutros (cercanos a 0)
  - Verde: Valores positivos (crecimiento)
- **Blues**: Para rankings y valores absolutos
- **Set2/Pastel1**: Para bancos en gráficos multi-línea
- **Set3**: Para pie charts

### Alturas de Gráficos
- **KPIs**: Auto
- **Gráficos principales**: 400-500px
- **Gráficos dinámicos**: `max(400, n_elementos * 20-25)`
- **Treemaps**: 500px
- **Heatmaps**: 600px

### Formato de Valores
- **Millones USD**: División por 1000, formato `$X,XXX M`
- **Porcentajes**: Multiplicación por 100, formato `XX.X%`
- **Crecimiento**: `+XX.X%` o `-XX.X%`

---

## Flujo de Trabajo

### 1. Descarga de Datos
```bash
python descargar.py
```
Descarga archivos Excel mensuales desde la Superintendencia de Bancos.

### 2. Procesamiento
```bash
python procesar_balance.py
python procesar_pyg.py
python crear_master.py  # Para otros archivos
```
Genera archivos Parquet en `master_data/`.

### 3. Ejecución del Dashboard
```bash
streamlit run app.py
```
Inicia el dashboard en http://localhost:8501

---

## Casos de Uso Principales

### 1. Validación de Datos
**Módulo**: Calidad
**Objetivo**: Verificar completitud antes de análisis
**Pasos**:
1. Revisar KPIs de calidad
2. Identificar períodos con datos faltantes
3. Validar ecuación contable

### 2. Análisis de Mercado
**Módulo**: Panorama
**Objetivo**: Entender estructura del sistema
**Pasos**:
1. Revisar KPIs del sistema
2. Analizar composición con treemap
3. Identificar bancos líderes

### 3. Análisis de Evolución
**Módulo**: Balance General
**Objetivo**: Tendencias temporales
**Pasos**:
1. Seleccionar cuenta de balance
2. Comparar múltiples bancos
3. Analizar heatmap de crecimiento

### 4. Análisis de Rentabilidad
**Módulo**: Perdidas y Ganancias
**Objetivo**: Evaluar resultados
**Pasos**:
1. Revisar KPIs de rentabilidad
2. Analizar cascada de márgenes
3. Comparar evolución entre bancos

---

## Optimizaciones Técnicas

### Caché de Streamlit
Todas las funciones de procesamiento usan `@st.cache_data` para:
- Evitar recálculos innecesarios
- Mejorar tiempo de respuesta
- Reducir uso de memoria

### Formato Parquet
- Almacenamiento columnar eficiente
- Compresión nativa
- Lectura rápida de columnas específicas

### Validación de Datos
- Filtrado de cuentas vacías
- Eliminación de duplicados
- Verificación de tipos de datos

---

## Limitaciones Conocidas

1. **Datos PYG**: Acumulados por año, requieren desacumulación
2. **Cobertura histórica**: Algunos bancos tienen datos desde 2008, no 2003
3. **Indicadores**: 32.67% de nulos en hoja INDICAD
4. **Banco Amazonas**: No existe en metadata actual

---

## Mantenimiento

### Actualización Mensual
1. Ejecutar `descargar.py` para nuevos datos
2. Re-ejecutar scripts de procesamiento
3. Verificar módulo de Calidad

### Limpieza de Caché
```bash
streamlit cache clear
```

### Actualización de Dependencias
```bash
pip install -r requirements.txt --upgrade
```

---

## Documentación Relacionada

| Documento | Descripción |
|-----------|-------------|
| [RESUMEN_PROYECTO.md](../RESUMEN_PROYECTO.md) | Resumen ejecutivo del proyecto |
| [CHANGELOG.md](../CHANGELOG.md) | Registro de cambios por versión |
| [README.md](README.md) | Índice de documentación técnica |
| [PROCESAMIENTO_PYG.md](PROCESAMIENTO_PYG.md) | Lógica de desacumulación de PYG |
| [MODULO_RENTABILIDAD.md](MODULO_RENTABILIDAD.md) | Especificación del módulo de rentabilidad |
| [MODULO_SERIES_TEMPORALES.md](MODULO_SERIES_TEMPORALES.md) | Especificación del módulo de balance |

---

## Próximos Pasos (Futuras Versiones)

### Funcionalidades Pendientes
- Exportación de gráficos a PDF/PNG
- Filtros avanzados por segmento de banco
- Alertas automáticas (detección de anomalías)
- Reportes programados

### Análisis Adicionales
- Descomposición temporal (tendencia + estacionalidad)
- Forecasting simple (proyecciones)
- Análisis de eficiencia operativa
- Comparación de estructura de resultados

### Datos Adicionales
- Integrar datos macroeconómicos
- Agregar tasas de interés del BCE
- Incluir indicadores de mercado

---

**Autor**: Dashboard Radar Bancario Ecuador
**Versión**: 4.0.0
**Fecha**: 26 de enero de 2026
**Estado**: ✅ Implementado y Documentado
