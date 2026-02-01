# Documentación - Radar Bancario Ecuador

Índice de documentación técnica del dashboard de Business Intelligence.

## 📋 Documentos Disponibles

### Guías de Usuario

| Documento | Descripción |
|-----------|-------------|
| [GUIA_RAPIDA.md](GUIA_RAPIDA.md) | Guía rápida para usar el sistema de descarga y procesamiento |
| [INSTRUCCIONES_DESCARGA.md](INSTRUCCIONES_DESCARGA.md) | Instrucciones detalladas para descargar datos |

### Especificaciones Técnicas

| Documento | Descripción |
|-----------|-------------|
| [ESTRUCTURA_EXCEL.md](ESTRUCTURA_EXCEL.md) | Estructura de archivos Excel de la Superintendencia |
| [BI_MASTER_FILES.md](BI_MASTER_FILES.md) | Especificación de archivos master consolidados |
| [VISUALIZACIONES.md](VISUALIZACIONES.md) | Diseño conceptual del dashboard (plan inicial) |
| [PROCESAMIENTO_PYG.md](PROCESAMIENTO_PYG.md) | Procesamiento de hoja PYG con desacumulación y suma móvil 12M |
| [SCRIPTS_PROCESAMIENTO.md](SCRIPTS_PROCESAMIENTO.md) | Documentación completa de todos los scripts de procesamiento |

### Visualizaciones Implementadas

| Documento | Descripción | Versión |
|-----------|-------------|---------|
| [MODULO_PANORAMA.md](MODULO_PANORAMA.md) | Módulo Panorama completo (Activos, Pasivos, Crecimiento) | 2.0 |
| [VISUALIZACION_CRECIMIENTO.md](VISUALIZACION_CRECIMIENTO.md) | Gráficos de crecimiento anual por banco (barras horizontales) | 1.0 |
| [MODULO_SERIES_TEMPORALES.md](MODULO_SERIES_TEMPORALES.md) | Módulo de series temporales avanzadas (3 visualizaciones) | 1.0 |
| [MODULO_RENTABILIDAD.md](MODULO_RENTABILIDAD.md) | Módulo de rentabilidad y resultados PYG (6 visualizaciones) | 1.0 |

## 📊 Estructura del Dashboard

### Módulos Principales

```
pages/
├── 0_Calidad.py             # Validación de calidad de datos
├── 1_Panorama.py            # Vista general del sistema
├── 2_Balance_General.py     # Análisis temporal de balance
└── 3_Perdidas_Ganancias.py  # Rentabilidad y resultados (PYG)
```

### Utilidades

```
utils/
├── data_loader.py      # Carga centralizada de datos
├── data_quality.py     # Funciones de validación
└── charts.py           # Componentes gráficos reutilizables
```

### Configuración

```
config/
└── indicator_mapping.py  # Mapeo de códigos contables
```

## 🎨 Guía de Visualizaciones

### Tipos de Gráficos Implementados

1. **KPI Cards** - Métricas principales del sistema
2. **Treemap Jerárquico** - Composición de activos con drill-down
3. **Barras Horizontales** - Rankings y comparaciones
4. **Barras de Crecimiento** - Variaciones anuales por banco
5. **Gráficos de Línea** - Series temporales y evolución
6. **Heatmap** - Crecimiento anual por banco
7. **Waterfall** - Cascada de formación de márgenes
8. **Pie Charts** - Composición porcentual

### Paleta de Colores

- **Primario**: Azul (`#1f77b4`)
- **Acento**: Naranja (`#ff7f0e`)
- **Éxito**: Verde (`#2ca02c`)
- **Alerta**: Rojo (`#d62728`)
- **Escala de Crecimiento**: RdYlGn (Rojo-Amarillo-Verde)

## 🔧 Convenciones de Código

### Funciones Cacheadas

Todas las funciones de procesamiento de datos usan `@st.cache_data`:

```python
@st.cache_data
def obtener_datos(df: pd.DataFrame, fecha) -> pd.DataFrame:
    """
    Descripción breve de la función.

    Args:
        df: DataFrame de entrada
        fecha: Fecha de análisis

    Returns:
        DataFrame procesado
    """
    # Implementación
    return resultado
```

### Códigos Contables

Usar siempre constantes de `config/indicator_mapping.py`:

```python
from config.indicator_mapping import CODIGOS_BALANCE

# Correcto
codigo = CODIGOS_BALANCE['activo_total']  # '1'

# Incorrecto (no usar strings directos)
codigo = '1'  # ❌
```

### Formato de Valores

- **Millones de USD**: Dividir por 1000
- **Porcentajes**: Multiplicar por 100
- **Formato de display**: `f"${valor:,.0f}M"` o `f"{valor:.1f}%"`

## 📐 Estándares de Layout

### Alturas de Gráficos

- **KPIs**: N/A (auto)
- **Gráficos principales**: 400-500px
- **Gráficos con muchos elementos**: `max(400, n_elementos * 20)`
- **Treemaps**: 500px
- **Tablas**: Auto con scroll

### Columnas de Streamlit

```python
# Dos columnas con proporción 2:1
col_left, col_right = st.columns([2, 1])

# Tres columnas iguales
col1, col2, col3 = st.columns(3)

# Cinco columnas para KPIs
col1, col2, col3, col4, col5 = st.columns(5)
```

## 🚀 Proceso de Desarrollo

### Agregar Nueva Visualización

1. **Documentar**: Crear archivo MD en `docs/`
2. **Implementar**: Agregar función en archivo de página
3. **Testear**: Verificar con datos reales
4. **Actualizar**: Modificar este README con el nuevo componente

### Modificar Visualización Existente

1. **Revisar documentación**: Leer el archivo MD correspondiente
2. **Hacer cambios**: Implementar mejoras
3. **Actualizar doc**: Modificar MD con cambios realizados
4. **Versionar**: Incrementar número de versión en doc

## 📝 Changelog

### Enero 2026

- **26/01/2026**: Reestructuración del dashboard (v4.0.0)
  - Simplificación de 8 a 4 módulos principales
  - Eliminación de módulos CAMEL, Comparador, Evolución, Perfil
  - Renombrado de módulos para mayor claridad
  - Documentación actualizada

- **26/01/2026**: Implementación de módulo Perdidas y Ganancias (v3.3.0)
  - 6 visualizaciones de rentabilidad
  - Procesamiento de datos PYG con desacumulación
  - Suma móvil de 12 meses para comparabilidad

- **25/01/2026**: Implementación de gráficos de crecimiento anual por banco (v1.0)
  - Barras horizontales ordenadas por crecimiento
  - Comparación vs mismo mes año anterior
  - Escala de colores RdYlGn
  - Aplicado a Cartera de Créditos y Depósitos

## 🔍 Referencias Técnicas

### Bibliotecas Principales

- **Streamlit**: Framework web - [Docs](https://docs.streamlit.io/)
- **Plotly**: Gráficos interactivos - [Docs](https://plotly.com/python/)
- **Pandas**: Manipulación de datos - [Docs](https://pandas.pydata.org/docs/)

### Fuentes de Datos

- **Superintendencia de Bancos del Ecuador**: https://www.superbancos.gob.ec/
- **Portal Estadístico**: https://www.superbancos.gob.ec/estadisticas/portalestudios/

---

**Última actualización**: 26 de enero de 2026
**Versión**: 2.0
