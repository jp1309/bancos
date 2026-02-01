# Módulo: Rentabilidad y Resultados (PYG)

## Descripción General

Módulo especializado en el análisis de pérdidas y ganancias del sistema bancario ecuatoriano. Permite visualizar márgenes de rentabilidad, evolución temporal y comparar resultados entre bancos.

## Estado: ✅ IMPLEMENTADO

- **Archivo**: `pages/7_PYG_Rentabilidad.py`
- **Nombre**: "💰 Rentabilidad y Resultados"
- **Posición**: Después del módulo Series Temporales
- **Fecha de Implementación**: 26 de enero de 2026
- **Versión**: 1.0

---

## Objetivos

1. **Visualizar Rentabilidad**: Mostrar indicadores clave de resultados del sistema
2. **Comparar Bancos**: Ranking y participación de mercado en rentabilidad
3. **Analizar Márgenes**: Cascada de formación del resultado
4. **Evolución Temporal**: Tendencias de rentabilidad a lo largo del tiempo
5. **Crecimiento**: Variación anual de indicadores de resultado

---

## Fuente de Datos

- **Archivo**: `master_data/pyg.parquet`
- **Registros**: 769,792
- **Bancos**: 24
- **Periodo**: Enero 2003 - Diciembre 2025
- **Columnas usadas**:
  - `valor_12m`: Suma móvil de 12 meses (principal para comparabilidad)
  - `valor_mes`: Valor del mes individual
  - `valor_acumulado`: Valor acumulado en el año (Excel original)

---

## Indicadores PYG Principales

```python
CUENTAS_PYG = {
    'MNI': 'Margen Neto de Intereses',
    'MBF': 'Margen Bruto Financiero',
    'MNF': 'Margen Neto Financiero',
    'MDI': 'Margen de Intermediación',
    'MOP': 'Margen Operacional',
    'GAI': 'Ganancia Antes de Impuestos',
    'GDE': 'Ganancia del Ejercicio',
}
```

### Jerarquía de Resultados

```
INGRESOS POR INTERESES
- GASTOS POR INTERESES
= MNI (Margen Neto de Intereses)

MNI + Comisiones - Pérdidas Financieras
= MBF (Margen Bruto Financiero)

MBF - Provisiones
= MNF (Margen Neto Financiero)

MNF - Gastos de Operación
= MDI (Margen de Intermediación)

MDI - Otras Pérdidas Operacionales
= MOP (Margen Operacional)

MOP - Otros Gastos
= GAI (Ganancia Antes de Impuestos)

GAI - Impuestos
= GDE (Ganancia del Ejercicio)
```

---

## Sección 1: KPIs del Sistema

### Descripción
4 métricas principales del sistema bancario en la fecha seleccionada.

### Visualización
```
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│ Margen Neto      │ │ Margen           │ │ Ganancia Antes   │ │ Ganancia del     │
│ Intereses        │ │ Operacional      │ │ Impuestos        │ │ Ejercicio        │
│                  │ │                  │ │                  │ │                  │
│  $5,234M         │ │  $1,890M         │ │  $1,456M         │ │  $1,123M         │
└──────────────────┘ └──────────────────┘ └──────────────────┘ └──────────────────┘
```

### Implementación
```python
df_fecha = df_pyg[df_pyg['fecha'] == fecha_seleccionada]

for codigo, nombre in CUENTAS_PYG.items():
    df_codigo = df_fecha[df_fecha['codigo'] == codigo]
    kpi_valor = df_codigo['valor_12m'].sum() / 1000  # Millones
```

### Características
- Suma de todos los bancos del sistema
- Valores en millones de USD
- Suma móvil 12 meses (valor_12m)
- Tooltips con descripción de cada indicador

---

## Sección 2: Ranking de Rentabilidad

### Descripción
Ranking de bancos ordenados por Ganancia del Ejercicio (GDE).

### Visualización
```
┌─────────────────────────────────────────────┐
│ Top 15 Bancos por Ganancia                  │
├─────────────────────────────────────────────┤
│ Pichincha      ████████████████████ $450M   │
│ Guayaquil      █████████████████ $380M      │
│ Pacifico       ████████████ $250M           │
│ Produbanco     ███████████ $230M            │
│ ...                                         │
└─────────────────────────────────────────────┘
```

### Características
- Barras horizontales ordenadas por valor
- Slider para seleccionar Top N (5 a 24)
- Escala de color azul (intensidad por valor)
- Valores en millones USD
- Suma móvil 12 meses

---

## Sección 3: Crecimiento Anual

### Descripción
Barras horizontales mostrando variación YoY de GDE y MOP por banco.

### Visualización
```
Ganancia del Ejercicio              Margen Operacional

Banco A  ████████ 25.3%            Banco C  ███████ 18.2%
Banco B  ██████ 15.8%              Banco A  ██████ 15.1%
Banco C  ████ 8.5%                 Banco B  ████ 10.3%
...      ... -5.2%                 ...      ... -2.1%
```

### Características
- Comparación vs mismo mes del año anterior
- Ordenamiento de mayor a menor crecimiento
- Escala de colores RdYlGn (Rojo-Amarillo-Verde)
- Rango de colores: -50% a +50%
- Línea de referencia en 0%
- Tooltip con valor absoluto y crecimiento

---

## Sección 4: Cascada de Márgenes

### Descripción
Gráfico waterfall mostrando la formación del resultado para un banco seleccionado.

### Visualización
```
      Formación del Resultado - Banco Pichincha

$600M │
      │  ┌─┐
$400M │  │ │ ┌─┐
      │  │ │ │ │  ┌─┐
$200M │  │ │ │ │  │ │  ┌─┐
      │  │ │ │ │  │ │  │ │  ┌─┐    ┌─┐
   0M └──┴─┴─┴─┴──┴─┴──┴─┴──┴─┴────┴─┴──────
      MNI MBF MNF MDI MOP   GAI    GDE
```

### Implementación
```python
fig_cascada = go.Figure(go.Waterfall(
    name="Margenes",
    orientation="v",
    measure=["relative"] * len(valores),
    x=etiquetas,
    y=valores,
    text=[f"${v:,.0f}M" for v in valores],
    textposition="outside",
))
```

### Características
- Selector de banco
- 7 etapas de márgenes (MNI → GDE)
- Valores en millones USD
- Conectores entre barras
- Etiquetas rotadas 45° para legibilidad

---

## Sección 5: Evolución Temporal Comparativa

### Descripción
Líneas múltiples comparando la evolución de un indicador para varios bancos.

### Visualización
```
┌───────────────────────────────────────────────────┐
│ Evolución: Ganancia del Ejercicio                 │
├───────────────────────────────────────────────────┤
│ $600M│                                             │
│      │                                      ─────  │
│ $400M│                              ──────         │
│      │                      ────────               │
│ $200M│              ────────                       │
│      │      ────────                               │
│    0M└──────────────────────────────────────────  │
│      2015   2017   2019   2021   2023   2025      │
│                                                    │
│      ─── Pichincha  ─── Guayaquil  ─── Pacifico   │
└───────────────────────────────────────────────────┘
```

### Características
- Multiselect para hasta 8 bancos
- Selector de indicador (MNI, MBF, MNF, MDI, MOP, GAI, GDE)
- Colores diferenciados por banco
- Hover unificado por fecha
- Suma móvil 12 meses para comparabilidad
- Leyenda horizontal debajo del gráfico

---

## Sección 6: Distribución de Rentabilidad

### Descripción
Pie chart mostrando participación de cada banco en la ganancia del sistema.

### Visualización
```
         Distribución de Ganancia por Banco

         ╱────────╲
        │  Pich.   │
        │  35.2%   │
         ╲────────╱
              │
       ╱──────┴──────╲
      │   Guay.      │
      │   28.1%      │
       ╲─────────────╱
              │
          [Otros...]
```

### Características
- Pie chart con hueco central (donut)
- Top 10 bancos + categoría "Otros"
- Solo valores positivos (ganancias)
- Porcentajes y valores absolutos
- Colores de paleta Set3
- Hover con detalles completos

---

## Funciones Principales

### 1. obtener_ranking_rentabilidad()
Obtiene ranking de bancos por rentabilidad en una fecha.

```python
@st.cache_data
def obtener_ranking_rentabilidad(df: pd.DataFrame, fecha, codigo: str) -> pd.DataFrame:
    df_fecha = df[(df['fecha'] == fecha) & (df['codigo'] == codigo)].copy()
    df_fecha['valor_millones'] = df_fecha['valor_12m'] / 1000
    df_fecha = df_fecha.sort_values('valor_millones', ascending=False)
    return df_fecha[['banco', 'valor_12m', 'valor_millones']]
```

### 2. obtener_cascada_margenes()
Prepara datos para gráfico waterfall de márgenes.

```python
@st.cache_data
def obtener_cascada_margenes(df: pd.DataFrame, banco: str, fecha) -> pd.DataFrame:
    codigos_cascada = ['MNI', 'MBF', 'MNF', 'MDI', 'MOP', 'GAI', 'GDE']

    df_filtrado = df[
        (df['banco'] == banco) &
        (df['fecha'] == fecha) &
        (df['codigo'].isin(codigos_cascada))
    ].copy()

    df_filtrado['valor_millones'] = df_filtrado['valor_12m'] / 1000
    return df_filtrado
```

### 3. obtener_crecimiento_anual_pyg()
Calcula crecimiento anual de un indicador.

```python
@st.cache_data
def obtener_crecimiento_anual_pyg(df: pd.DataFrame, codigo: str,
                                   fecha_actual, fecha_anterior) -> pd.DataFrame:
    df_actual = df[(df['fecha'] == fecha_actual) & (df['codigo'] == codigo)]
    df_anterior = df[(df['fecha'] == fecha_anterior) & (df['codigo'] == codigo)]

    df_merged = df_actual.merge(df_anterior, on='banco', suffixes=('_actual', '_anterior'))

    df_merged['crecimiento'] = (
        (df_merged['valor_12m_actual'] - df_merged['valor_12m_anterior']) /
        df_merged['valor_12m_anterior'].abs() * 100
    )

    return df_merged
```

---

## Filtros y Controles

### Sidebar
- **Fecha**: Selector de mes/año
- **Comparación anual**: Automática (fecha - 12 meses)
- **Info**: Fecha seleccionada, bancos disponibles

### Interactivos
- **Ranking**: Slider para Top N bancos
- **Cascada**: Selector de banco
- **Evolución**: Multiselect de bancos + selector de indicador

---

## Consideraciones Técnicas

### Uso de valor_12m

**Razón**: Los datos de PYG son acumulados mes a mes en el año. Para comparar cualquier mes con otro, usamos suma móvil de 12 meses.

**Ventaja**:
- Comparabilidad entre cualquier mes
- Evita estacionalidad
- Comparable con valor de diciembre (total anual)

**Ejemplo**:
```
Marzo 2024 vs Septiembre 2024:
- Marzo: suma de 12 meses previos (abr 2023 - mar 2024)
- Sept: suma de 12 meses previos (oct 2023 - sept 2024)
Ambos representan "últimos 12 meses"
```

### Manejo de Valores Negativos

Los márgenes pueden ser negativos (pérdidas). El código maneja esto:
- Ranking: Ordena de mayor a menor (los más negativos al final)
- Pie chart: Solo muestra valores positivos
- Crecimiento: Usa `.abs()` en denominador para evitar errores

### Caché

Todas las funciones de procesamiento usan `@st.cache_data` para optimizar rendimiento.

---

## Resumen de Visualizaciones

| # | Visualización | Tipo | Datos Usados | Estado |
|---|---------------|------|--------------|--------|
| 1 | KPIs del Sistema | Metrics | valor_12m suma | ✅ |
| 2 | Ranking Rentabilidad | Bar horizontal | valor_12m por banco | ✅ |
| 3 | Crecimiento Anual | Bar horizontal | valor_12m YoY | ✅ |
| 4 | Cascada Márgenes | Waterfall | valor_12m por código | ✅ |
| 5 | Evolución Temporal | Line multi | valor_12m serie | ✅ |
| 6 | Distribución | Pie chart | valor_12m % | ✅ |

---

## Próximos Pasos (Futuras Versiones)

- Agregar análisis de eficiencia (gastos/ingresos)
- Comparar estructura de resultados entre bancos
- Análisis de descomposición de márgenes
- Proyección de rentabilidad (forecasting simple)

---

**Autor**: Dashboard Radar Bancario Ecuador
**Fecha**: 26 de enero de 2026
**Versión**: 1.0
**Estado**: ✅ Implementado (6 visualizaciones)
