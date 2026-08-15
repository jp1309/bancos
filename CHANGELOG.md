Nota: Este changelog incluye entradas historicas de modulos y archivos que ya no existen en el repo actual.

# Changelog - Sistema de Inteligencia Financiera

Registro de cambios y mejoras del dashboard de Business Intelligence.

## [4.4.0] - 2026-08-14

### Datos

- Publicado y validado el corte de julio de 2026 en Balance, PyG y CAMEL.
- Confirmados 23 bancos en el último mes de los tres datasets.
- Normalizados nombres equivalentes con acentos, mayúsculas y Unicode para conservar series continuas.

### Automatización

- Eliminados los tokens de OneDrive codificados: el descargador usa los enlaces vigentes del DOM.
- Añadidos reintentos HTTP y descarga segura mediante Chrome cuando el portal entrega una cadena TLS incompleta.
- Los no-op se resuelven antes de descargar 23 ZIP si el portal aún anuncia el corte anterior.
- Se reutiliza una fuente local ya validada al reintentar el ETL y cada run usa un staging único.
- Revisión diaria del 6 al 20, exclusión de concurrencia y timeout de 30 minutos.
- Nuevas pruebas para enlaces permitidos, publicaciones rezagadas/parciales y nombres canónicos.
- La caché de Streamlit incorpora la huella de cada archivo y se invalida con cada publicación.

## [4.3.0] - 2026-07-18

### Datos y automatización

- Publicado y validado el corte de junio de 2026 para Balance, PyG y CAMEL.
- La descarga valida 23 ZIP/XLSX, las tres hojas requeridas y la fecha interna uniforme.
- El pipeline trata la fuente sin avance como no-op mediante código de salida `2`.
- Los tres procesadores usan escritura atómica y el orquestador restaura los artefactos anteriores ante fallos.
- Nueva puerta de publicación para esquema, fecha, continuidad mensual, cobertura, duplicados, metadata e historia.
- Workflow con permisos explícitos de escritura y reintentos del 6 al 20 de cada mes.

### Aplicación

- Portada alimentada por `metadata.json`, sin cifras mensuales escritas a mano.
- Cobertura visible y validada de 23 bancos hasta junio de 2026.
- Reducción de memoria mediante categorías y `groupby(observed=True)`.

### Documentación

- Reescritos README, inicio rápido, contribución y ficha del proyecto.
- Añadidos runbook de operación/recuperación, diccionario de datos y arquitectura.
- Consolidado el índice de fuentes de verdad y separadas las notas históricas.

## [4.2.0] - 2026-01-28

### Rediseño de Interfaz
- **Nuevo nombre**: Sistema de Inteligencia Financiera - Banca Ecuador
- **Página principal rediseñada** (`app.py` → `Inicio.py`):
  - KPIs principales visibles en la portada (bancos, años, meses, última actualización)
  - Introducción más amigable para usuarios finales
  - Botones de acceso rápido a módulos principales
  - Footer mejorado con información técnica (emoji 🧠 en lugar de ❤️)
  - Eliminada referencia al módulo de Calidad de Datos
  - Renombrado archivo principal a `Inicio.py` para mejor identificación en sidebar

- **Módulo Calidad de Datos archivado**: Movido a `archived_pages/` para uso técnico interno

### Agregado
- **Módulo Panorama - Nueva sección de Pasivos**:
  - Treemap jerárquico de Pasivos y Patrimonio con drill-down por banco
  - Ranking de bancos por Pasivos Totales (código '2')
  - Composición detallada: Obligaciones con el Público, Obligaciones Financieras, Valores en Circulación, Otros Pasivos, Patrimonio
  - Misma estructura visual que sección de Activos para consistencia

### Removido
- **Módulo Panorama**:
  - Eliminados gráficos de pastel de "Composición del Sistema"
  - Removida visualización de Estructura de Activos (pie chart)
  - Removida visualización de Estructura de Pasivos y Patrimonio (pie chart)
  - Los treemaps proporcionan información más detallada y navegable

### Optimizado
- **Reducción del tamaño de datos**: De 37.3 MB a 29.1 MB (ahorro del 22%)
  - Eliminados archivos parquet innecesarios: `indicadores.parquet`, `cartera.parquet`, `fuentes_usos.parquet`
  - Solo se mantienen las 3 hojas esenciales: BAL, PYG, CAMEL

- **Simplificación de scripts**:
  - Eliminado `crear_master.py` (procesaba 8 hojas)
  - Solo 3 scripts de procesamiento necesarios:
    - `procesar_balance.py` → balance.parquet (18 MB)
    - `procesar_pyg.py` → pyg.parquet (9.5 MB)
    - `procesar_camel.py` → camel.parquet (1.6 MB)

- **Código más limpio**:
  - Eliminadas funciones no utilizadas en `data_loader.py`
  - Simplificada página `0_Calidad.py` para cargar solo datos esenciales
  - Actualizada toda la documentación

### Mejorado
- **Heatmap CAMEL mensual**: Ahora muestra todos los meses con selector de rango de fechas
- **Ordenamiento por tamaño**: Bancos ordenados por activos totales (Pichincha en la parte superior)
- **Formato de indicadores**: Todos los indicadores con 1 decimal
- **Sistema de colores consistentes**:
  - Cada banco tiene un color único asignado permanentemente
  - Los colores se mantienen consistentes en todas las visualizaciones de todos los módulos
  - Paleta de 24 colores distinguibles basada en mejores prácticas de accesibilidad
  - Implementado en: rankings, gráficos de línea, treemaps, y todas las visualizaciones

### Técnico
- Los archivos Excel contienen muchas hojas, pero el dashboard solo usa 3: BAL, PYG, CAMEL
- Las hojas INDICAD, INDIC CARTERA, ESTRUC CART, FUENTES USOS, REFINA REES no se utilizan
- Procesamiento más rápido al leer solo las hojas necesarias
- Dashboard enfocado en 4 módulos principales para usuarios finales

---

## [4.1.0] - 2026-01-26

### Agregado
- **Nuevo Módulo: Indicadores CAMEL** (`pages/4_CAMEL.py`)
  - 5 visualizaciones implementadas:
    1. **KPIs del Sistema**: Solvencia, Morosidad, Cobertura, ROE, Liquidez
    2. **Análisis por Indicador**: Ranking de bancos por categoría CAMEL
    3. **Composición de Cartera**: Treemap por banco y pie chart del sistema
    4. **Evolución Temporal**: Comparación multi-banco de indicadores
    5. **Heatmap Anual**: Evolución histórica de indicadores por banco

- **Procesamiento de Hoja CAMEL** (`procesar_camel.py`)
  - Extracción de 39 indicadores financieros
  - Categorización por dimensiones CAMEL:
    - C: Capital (Solvencia)
    - A: Activos (Morosidad, Cobertura, Composición)
    - M: Management (Eficiencia operativa)
    - E: Earnings (ROA, ROE)
    - L: Liquidity (Índice de liquidez)
  - Composición de cartera por tipo de crédito (8 categorías)

### Datos Generados
- **`master_data/camel.parquet`**
  - 233,680 registros
  - 24 bancos
  - 276 fechas (enero 2003 - diciembre 2025)
  - 39 indicadores únicos
  - 6 categorías CAMEL

---

## [4.0.0] - 2026-01-26

### Reestructuración del Dashboard
- **Simplificación de módulos**: Reducción de 8 a 4 módulos principales
- **Estructura final**:
  - **Módulo 0**: Calidad de Datos
  - **Módulo 1**: Panorama del Sistema
  - **Módulo 2**: Balance General (anteriormente Series Temporales)
  - **Módulo 3**: Perdidas y Ganancias (anteriormente Rentabilidad)

### Removido
- **Módulo CAMEL**: Eliminado análisis por dimensiones CAMEL
- **Módulo Comparador**: Eliminado benchmarking entre bancos
- **Módulo Evolución**: Eliminado series temporales básicas
- **Módulo Perfil**: Eliminado fichas individuales por banco

### Mejorado
- Renombrado módulo "Series Temporales" a "Balance General" para mayor claridad
- Renombrado módulo "Rentabilidad y Resultados" a "Perdidas y Ganancias"
- Actualización de íconos y títulos en módulos

---

## [3.3.0] - 2026-01-26

### Agregado
- **Nuevo Módulo: Rentabilidad y Resultados** (`pages/7_Rentabilidad.py`)
  - 6 visualizaciones implementadas:
    1. **KPIs del Sistema**: 4 métricas principales (MNI, MOP, GAI, GDE)
    2. **Ranking de Rentabilidad**: Top bancos por ganancia del ejercicio
    3. **Crecimiento Anual**: Variación YoY de GDE y MOP por banco
    4. **Cascada de Márgenes**: Formación del resultado por banco
    5. **Evolución Temporal**: Comparación de múltiples bancos en el tiempo
    6. **Distribución**: Participación en ganancia del sistema (pie chart)
  - Usa datos de suma móvil 12 meses (valor_12m) para comparabilidad
  - Selector de fecha y banco
  - Comparación automática vs año anterior

- **Procesamiento de Hoja PYG (Pérdidas y Ganancias)** (`procesar_pyg.py`)
  - Extracción de datos acumulados de los archivos Excel
  - Lógica de desacumulación mensual (valor de cada mes individual)
  - Cálculo de suma móvil de 12 meses para comparabilidad
  - Códigos personalizados para cuentas resumen:
    - MNI: Margen Neto de Intereses
    - MBF: Margen Bruto Financiero
    - MNF: Margen Neto Financiero
    - MDI: Margen de Intermediación
    - MOP: Margen Operacional
    - GAI: Ganancia/Pérdida Antes de Impuestos
    - GDE: Ganancia/Pérdida del Ejercicio

### Datos Generados
- **`master_data/pyg.parquet`**
  - 769,792 registros
  - 24 bancos
  - 276 fechas (enero 2003 - diciembre 2025)
  - 128 cuentas únicas
  - Columnas: banco, fecha, codigo, cuenta, valor_acumulado, valor_mes, valor_12m
  - 95.6% de registros con valor_12m calculado

### Técnico
- Función `desacumular_valores()`: Convierte valores acumulados a mensuales
- Función `calcular_suma_movil_12m()`: Rolling sum de 12 meses por banco/código
- Manejo de filas resumen sin código (filas 30, 80, 97, 107, 120, 133, 140)

---

## [3.2.0] - 2026-01-25

### Agregado
- **Nuevo Módulo: Series Temporales Avanzadas** (`pages/6_Series_Temporales.py`)
  - 5 visualizaciones interactivas implementadas:
    1. **Evolución Comparativa**: Líneas múltiples para hasta 10 bancos
       - Modos: Valores Absolutos, Indexado (Base 100), Participación %
       - Opción de incluir Total Sistema
    2. **Heatmap Temporal**: Matriz Año × Mes de crecimiento mensual
       - Escala de colores RdYlGn centrada en 0
       - Selección de banco o sistema completo
    3. **Correlación entre Variables**: Scatter plot con regresión
       - Color por año (gradiente temporal)
       - Métricas: R, R², interpretación
    4. **Velocidad de Crecimiento**: Barras por período
       - Trimestral o anual
       - Estadísticas: promedio, max, min, volatilidad
    5. **Ranking Dinámico**: Race chart animado
       - Top 10 bancos por año
       - Control de reproducción

### Documentación
- Actualizado `docs/MODULO_SERIES_TEMPORALES.md` con estado de implementación
- Actualizado índice de documentación

---

## [3.1.0] - 2026-01-25

### Agregado
- **Visualización de Crecimiento Anual por Banco** en módulo Panorama
  - Barras horizontales ordenadas de mayor a menor crecimiento
  - Comparación del mes seleccionado vs mismo mes del año anterior
  - Escala de colores RdYlGn (Rojo-Amarillo-Verde)
  - Aplicado a:
    - Cartera de Créditos
    - Depósitos del Público
  - Altura dinámica según número de bancos
  - Línea de referencia en 0% para identificar crecimiento/decrecimiento

### Documentación
- Creada carpeta `docs/` para documentación técnica
- Agregado `docs/VISUALIZACION_CRECIMIENTO.md` con especificación completa
- Agregado `docs/README.md` como índice de documentación
- Actualizado README principal con nueva estructura

### Mejorado
- Ranking de bancos ahora muestra todos los bancos (antes solo top 10)
- Altura del ranking ajustada dinámicamente según cantidad de bancos

### Técnico
- Implementado merge de DataFrames para calcular variaciones anuales
- Uso de `fecha_anterior` (12 meses atrás) para comparaciones
- Ordenamiento ascendente en eje Y para barras horizontales
- Configuración de escala de colores: cmin=-10, cmax=30

---

## [3.0.0] - 2026-01-24

### Agregado
- Dashboard multipage con 6 módulos
- Procesamiento de datos de Balance General
- Sistema de carga con validación
- Visualizaciones interactivas con Plotly

### Módulos Implementados
1. **Calidad de Datos** - Validación y métricas
2. **Panorama** - Vista general del sistema
3. **CAMEL** - Análisis por dimensiones
4. **Comparador** - Benchmarking entre bancos
5. **Evolución** - Series temporales
6. **Perfil** - Fichas individuales

### Infraestructura
- Arquitectura basada en Streamlit
- Almacenamiento en formato Parquet
- Sistema de caché para optimización
- Mapeo de códigos contables

---

## [2.0.0] - 2026-01-23

### Agregado
- Script `crear_master.py` para consolidar datos
- Procesamiento de 4 hojas Excel:
  - Balance General (BAL)
  - Indicadores (INDICAD)
  - Estructura de Cartera (CARTERA)
  - Fuentes y Usos (FUENTES_USOS)

### Mejorado
- Sistema de descarga automática
- Detección de archivos duplicados
- Validación de estructura de datos

---

## [1.0.0] - 2026-01-20

### Primera Versión
- Script de descarga `descargar.py`
- Descarga automática desde Superintendencia de Bancos
- Organización por año y mes
- 276 archivos históricos (enero 2003 - diciembre 2025)

---

## Formato

Este changelog sigue [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y el proyecto adhiere a [Semantic Versioning](https://semver.org/lang/es/).

### Tipos de Cambios
- `Agregado` - Nuevas funcionalidades
- `Mejorado` - Mejoras en funcionalidades existentes
- `Cambiado` - Cambios en funcionalidades existentes
- `Deprecado` - Funcionalidades que serán removidas
- `Removido` - Funcionalidades eliminadas
- `Corregido` - Corrección de bugs
- `Seguridad` - Vulnerabilidades corregidas

---

**Última actualización**: 26 de enero de 2026
