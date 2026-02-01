# Módulo Panorama - Documentación Técnica

## Descripción General

El módulo Panorama proporciona una vista general completa del sistema bancario ecuatoriano, con análisis tanto de Activos como de Pasivos y Patrimonio.

**Archivo**: `pages/1_Panorama.py`
**Versión**: 2.0
**Última actualización**: 28 de enero de 2026

---

## Estructura del Módulo

### 1. KPIs Principales del Sistema

**Ubicación**: Parte superior de la página

**Métricas mostradas**:
- Total Activos (código '1')
- Cartera de Créditos (código '14')
- Depósitos del Público (código '21')
- Patrimonio (código '3')
- Bancos Activos (conteo único)

**Características**:
- Valores en millones de USD (formato `$X,XXX M`)
- Delta porcentual vs año anterior (12 meses atrás)
- Codificación de colores para variaciones positivas/negativas

---

### 2. Análisis de Activos

#### 2.1 Treemap Jerárquico de Activos

**Función**: `obtener_datos_treemap_jerarquico(df, fecha, tipo='activos')`

**Jerarquía de datos**:
```
Sistema
└── Banco (código '1' - Activo Total)
    ├── Fondos Disponibles (código '11')
    ├── Inversiones (código '13')
    ├── Cartera de Créditos (código '14')
    ├── Cuentas por Cobrar (código '16')
    ├── Bienes Realizables (código '17')
    ├── Propiedades y Equipo (código '18')
    └── Otros Activos (código '19')
```

**Interactividad**:
- Clic en un banco para ver drill-down de composición
- Hover para ver valores absolutos y porcentajes
- Escala de colores automática por tamaño

#### 2.2 Ranking por Activos Totales

**Función**: `obtener_ranking_bancos(df, fecha, codigo='1', top_n=50)`

**Características**:
- Barras horizontales ordenadas de mayor a menor
- Muestra todos los bancos del sistema (no solo top 10)
- Altura dinámica: `max(400, n_bancos * 25)` pixeles
- Formato: `$X,XXX M`

---

### 3. Análisis de Pasivos y Patrimonio

#### 3.1 Treemap Jerárquico de Pasivos

**Función**: `obtener_datos_treemap_jerarquico(df, fecha, tipo='pasivos')`

**Jerarquía de datos**:
```
Sistema
└── Banco (código '2' + '3' - Pasivo Total + Patrimonio)
    ├── Obligaciones con el Público (código '21')
    ├── Cuentas por Pagar (código '25')
    ├── Obligaciones Financieras (código '26')
    ├── Valores en Circulación (código '27')
    ├── Otros Pasivos (código '29')
    └── Patrimonio (código '3')
```

**Lógica especial**:
- El nivel raíz suma Pasivo Total (código '2') + Patrimonio (código '3')
- Esto permite visualizar la estructura completa de financiamiento del banco
- El patrimonio se muestra como un componente más de la estructura

#### 3.2 Ranking por Pasivos Totales

**Características**:
- Usa código '2' (Pasivo Total, sin incluir patrimonio)
- Mismo formato que ranking de activos
- Permite comparar el nivel de apalancamiento de cada banco

---

### 4. Crecimiento Anual por Banco

**Sección**: Gráficos de barras horizontales comparativos

#### 4.1 Cartera de Créditos

**Código**: '14'
**Cálculo**: `(Valor_actual - Valor_año_anterior) / Valor_año_anterior * 100`

**Características**:
- Ordenamiento ascendente (menor a mayor crecimiento)
- Escala de colores RdYlGn (Rojo-Amarillo-Verde)
- Rango: -10% (rojo) a +30% (verde)
- Línea de referencia en 0%

#### 4.2 Depósitos del Público

**Código**: '21'
**Mismas características** que Cartera de Créditos

**Interpretación**:
- Verde intenso: Crecimiento > 20%
- Amarillo: Crecimiento moderado (0-10%)
- Rojo: Decrecimiento o crecimiento < 0%

---

## Funciones Clave

### `calcular_metricas_sistema(df, fecha)`

Calcula las métricas agregadas del sistema para una fecha específica.

**Retorna**: Diccionario con:
- `total_activos`: Suma de activos del sistema (en millones)
- `total_cartera`: Suma de cartera de créditos (en millones)
- `total_depositos`: Suma de depósitos del público (en millones)
- `total_patrimonio`: Suma de patrimonio (en millones)
- `fondos_disponibles`: Suma de fondos disponibles (en millones)
- `num_bancos`: Cantidad de bancos únicos

### `obtener_datos_treemap_jerarquico(df, fecha, tipo='activos')`

Prepara datos jerárquicos para visualización en treemap.

**Parámetros**:
- `df`: DataFrame con datos de balance
- `fecha`: Fecha para filtrar
- `tipo`: 'activos' o 'pasivos'

**Proceso**:
1. Filtra datos por fecha
2. Construye nivel 1 (bancos) según tipo:
   - Activos: código '1'
   - Pasivos: suma de códigos '2' + '3'
3. Construye nivel 2 (cuentas de 2 dígitos)
4. Calcula participaciones porcentuales
5. Retorna DataFrame con columnas: `labels`, `parents`, `values`, `tipo`, `id`, `participacion`

### `obtener_ranking_bancos(df, fecha, codigo, top_n=10)`

Obtiene ranking de bancos por una cuenta específica.

**Parámetros**:
- `df`: DataFrame con datos de balance
- `fecha`: Fecha para filtrar
- `codigo`: Código de cuenta contable
- `top_n`: Cantidad de bancos a incluir

**Retorna**: DataFrame con columnas: `banco`, `valor`, `valor_millones`

### `calcular_concentracion_hhi(df, fecha)`

Calcula el índice Herfindahl-Hirschman de concentración de mercado.

**Fórmula**: HHI = Σ(participación_i)²

**Interpretación**:
- HHI < 1500: Mercado no concentrado
- 1500 ≤ HHI < 2500: Mercado moderadamente concentrado
- HHI ≥ 2500: Mercado altamente concentrado

**Nota**: Esta función está implementada pero no se visualiza actualmente.

---

## Códigos Contables Utilizados

### Activos
| Código | Descripción |
|--------|-------------|
| `'1'` | Activo Total |
| `'11'` | Fondos Disponibles |
| `'13'` | Inversiones |
| `'14'` | Cartera de Créditos |
| `'16'` | Cuentas por Cobrar |
| `'17'` | Bienes Realizables |
| `'18'` | Propiedades y Equipo |
| `'19'` | Otros Activos |

### Pasivos
| Código | Descripción |
|--------|-------------|
| `'2'` | Pasivo Total |
| `'21'` | Obligaciones con el Público (Depósitos) |
| `'25'` | Cuentas por Pagar |
| `'26'` | Obligaciones Financieras |
| `'27'` | Valores en Circulación |
| `'29'` | Otros Pasivos |

### Patrimonio
| Código | Descripción |
|--------|-------------|
| `'3'` | Patrimonio |

---

## Convenciones de Diseño

### Colores
- **Treemap de Activos**: Escala de colores automática (blues)
- **Treemap de Pasivos**: Escala de colores automática (oranges)
- **Crecimiento YoY**: Escala RdYlGn (-10% a +30%)

### Formatos
- **Valores monetarios**: `$X,XXX M` (millones de USD)
- **Porcentajes**: `X.X%` (1 decimal)
- **Fechas**: `Mes YYYY` (ej: "Diciembre 2025")

### Alturas de Gráficos
- **Treemaps**: 500px fijo
- **Rankings**: Dinámico - `max(400, n_bancos * 25)` pixeles
- **Crecimiento YoY**: Dinámico - `max(400, n_bancos * 20)` pixeles

---

## Mejoras Implementadas (v2.0)

### Agregado
1. **Sección completa de Pasivos y Patrimonio**
   - Treemap jerárquico con drill-down
   - Ranking por pasivos totales
   - Composición detallada de obligaciones

2. **Función `obtener_datos_treemap_jerarquico()` mejorada**
   - Parámetro `tipo` para seleccionar activos o pasivos
   - Lógica especializada para cada tipo
   - Mayor flexibilidad para futuros cambios

### Removido
1. **Gráficos de pastel de composición**
   - Eliminado pie chart de Estructura de Activos
   - Eliminado pie chart de Estructura de Pasivos/Patrimonio
   - Razón: Los treemaps proporcionan información más rica y navegable

### Mantenido
- KPIs principales del sistema
- Análisis de crecimiento anual (Cartera y Depósitos)
- Estructura visual consistente entre secciones

---

## Uso del Módulo

### Navegación
1. Seleccionar fecha de análisis en el sidebar
2. Explorar KPIs del sistema en la parte superior
3. Navegar por las secciones:
   - **Activos**: Treemap + Ranking
   - **Pasivos**: Treemap + Ranking
   - **Crecimiento**: Cartera + Depósitos

### Interacción con Treemaps
1. **Vista inicial**: Muestra todos los bancos con tamaño proporcional
2. **Clic en banco**: Expande para mostrar composición interna
3. **Hover**: Muestra valores exactos y porcentajes
4. **Zoom**: Permite navegar por diferentes niveles jerárquicos

---

## Dependencias

### Librerías
```python
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
```

### Módulos internos
```python
from utils.data_loader import cargar_balance, obtener_fechas_disponibles
from utils.charts import (
    render_kpi_card,
    crear_ranking_barras,
    crear_treemap,
)
from config.indicator_mapping import CODIGOS_BALANCE
```

---

## Notas Técnicas

### Rendimiento
- Todas las funciones de procesamiento usan `@st.cache_data`
- Los treemaps pueden tener latencia con datasets grandes (>1M registros)
- Se recomienda limitar drill-down a 2 niveles máximo

### Validación de Datos
- Se filtran valores `NaN` y valores `<= 0`
- Se valida existencia de códigos contables antes de procesar
- Se maneja el caso de bancos sin datos para una fecha específica

### Escalabilidad
- La función `obtener_datos_treemap_jerarquico()` puede extenderse para incluir más niveles
- Los códigos de cuentas están centralizados en `config/indicator_mapping.py`
- Fácil agregar nuevas secciones siguiendo el patrón existente

---

**Autor**: Sistema de Inteligencia Financiera - Banca Ecuador
**Versión del documento**: 1.0
**Fecha**: 28 de enero de 2026
