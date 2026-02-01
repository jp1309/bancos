# Procesamiento de Hoja PYG (Pérdidas y Ganancias)

## Descripción General

Script para procesar la hoja PYG de los archivos Excel de la Superintendencia de Bancos del Ecuador. Esta hoja contiene información de pérdidas y ganancias con una característica especial: los datos son **acumulados mes a mes** dentro de cada año.

## Archivo

- **Script**: `procesar_pyg.py`
- **Salida**: `master_data/pyg.parquet`
- **Fecha de creación**: 26 de enero de 2026

---

## Lógica de Datos

### Problema: Datos Acumulados

En los archivos Excel originales, los valores del estado de resultados son acumulados:

```
Enero:     $100 (solo enero)
Febrero:   $180 (enero + febrero = $100 + $80)
Marzo:     $250 (enero + febrero + marzo = $100 + $80 + $70)
...
Diciembre: $1,200 (total del año)
Enero siguiente: $90 (reinicia, nuevo año)
```

### Solución: Desacumulación + Suma Móvil

El script implementa dos transformaciones:

1. **Desacumulación**: Obtener el valor de cada mes individual
2. **Suma Móvil 12M**: Calcular suma de últimos 12 meses para comparabilidad

---

## Estructura de la Hoja PYG

```
     A          B                    C         D         E    ...
1  [vacío]    [vacío]             [vacío]   [vacío]   [vacío]
2  [vacío]    [vacío]             [vacío]   [vacío]   [vacío]
3  [vacío]    [vacío]             [vacío]   [vacío]   [vacío]
4  [vacío]    [vacío]             [vacío]   [vacío]   [vacío]
5  [vacío]    [vacío]             FECHA_1   FECHA_2   FECHA_3  ...
6  CODIGO_1   NOMBRE_CUENTA_1     valor     valor     valor
7  CODIGO_2   NOMBRE_CUENTA_2     valor     valor     valor
...
```

- **Códigos**: Columna A, desde fila 6
- **Nombres**: Columna B
- **Datos**: Desde columna C
- **Fechas**: Fila 5, desde columna C

---

## Cuentas Resumen

Las siguientes filas tienen `--` como código y son cuentas resumen. Se les asigna códigos personalizados:

| Fila | Nombre Original | Código Asignado |
|------|-----------------|-----------------|
| 30 | MARGEN NETO DE INTERESES | MNI |
| 80 | MARGEN BRUTO FINANCIERO | MBF |
| 97 | MARGEN NETO FINANCIERO | MNF |
| 107 | MARGEN DE INTERMEDIACIÓN | MDI |
| 120 | MARGEN OPERACIONAL | MOP |
| 133 | GANANCIA O PÉRDIDA ANTES DE IMPUESTOS | GAI |
| 140 | GANANCIA O PÉRDIDA DEL EJERCICIO | GDE |

---

## Algoritmo de Desacumulación

```python
def desacumular_valores(df: pd.DataFrame) -> pd.DataFrame:
    """
    Desacumula los valores para obtener el valor de cada mes individual.

    Lógica:
    - Enero: valor_mes = valor_acumulado (primer mes del año)
    - Feb-Dic: valor_mes = valor_acumulado - valor_acumulado_mes_anterior
    """
    df = df.sort_values(['banco', 'codigo', 'fecha']).copy()
    df['ano'] = df['fecha'].dt.year
    df['mes'] = df['fecha'].dt.month

    # Valor del mes anterior (dentro del mismo banco, código y año)
    df['valor_anterior'] = df.groupby(['banco', 'codigo', 'ano'])['valor_acumulado'].shift(1)

    # Desacumular
    df['valor_mes'] = np.where(
        (df['mes'] == 1) | (df['valor_anterior'].isna()),
        df['valor_acumulado'],
        df['valor_acumulado'] - df['valor_anterior']
    )

    return df
```

### Ejemplo Visual

| Fecha | valor_acumulado | valor_mes |
|-------|-----------------|-----------|
| 2024-01 | 100 | 100 (enero, usar directo) |
| 2024-02 | 180 | 80 (180 - 100) |
| 2024-03 | 250 | 70 (250 - 180) |
| 2024-12 | 1200 | 150 (1200 - 1050) |
| 2025-01 | 90 | 90 (nuevo año, usar directo) |

---

## Algoritmo de Suma Móvil 12 Meses

```python
def calcular_suma_movil_12m(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula la suma móvil de 12 meses para cada banco/código.
    Esto permite comparar cualquier mes con cualquier otro.
    """
    df = df.sort_values(['banco', 'codigo', 'fecha']).copy()

    df['valor_12m'] = df.groupby(['banco', 'codigo'])['valor_mes'].transform(
        lambda x: x.rolling(window=12, min_periods=12).sum()
    )

    return df
```

### Ventaja del valor_12m

Permite comparar meses no homólogos:
- Marzo 2024 vs Septiembre 2024: Ambos tienen suma de 12 meses previos
- Evita problemas de estacionalidad
- Comparable directamente con el valor de diciembre (total anual)

---

## Columnas del Archivo de Salida

| Columna | Tipo | Descripción |
|---------|------|-------------|
| banco | str | Nombre del banco |
| fecha | datetime | Fecha del registro |
| codigo | str | Código de cuenta (o código personalizado para resumen) |
| cuenta | str | Nombre de la cuenta |
| valor_acumulado | float | Valor original del Excel (acumulado en el año) |
| valor_mes | float | Valor desacumulado del mes individual |
| valor_12m | float | Suma móvil de últimos 12 meses (NaN si < 12 meses) |

---

## Estadísticas del Archivo Generado

```
Registros totales:     769,792
Bancos:                24
Fechas:                276 (enero 2003 - diciembre 2025)
Cuentas únicas:        128
Tamaño archivo:        ~9.4 MB

Registros con valor_12m: 95.6%
```

---

## Uso en el Dashboard

### Cargar Datos

```python
from utils.data_loader import cargar_pyg

df_pyg, calidad = cargar_pyg()

# Columnas disponibles
print(df_pyg.columns)
# ['banco', 'fecha', 'codigo', 'cuenta', 'valor_acumulado', 'valor_mes', 'valor_12m']
```

### Ejemplos de Consulta

```python
# Ganancia del ejercicio (GDE) para un banco específico
df_gde = df_pyg[df_pyg['codigo'] == 'GDE']

# Comparar márgenes entre bancos
codigos_margen = ['MNI', 'MBF', 'MNF', 'MDI', 'MOP']
df_margenes = df_pyg[df_pyg['codigo'].isin(codigos_margen)]

# Usar valor_12m para comparaciones temporales justas
df_reciente = df_pyg[df_pyg['fecha'] == df_pyg['fecha'].max()]
```

---

## Cuentas Principales

### Jerarquía de Resultados

```
41 - INTERESES CAUSADOS
42 - COMISIONES CAUSADAS
─── MNI (Margen Neto de Intereses)
43 - PÉRDIDAS FINANCIERAS
44 - PROVISIONES
─── MBF (Margen Bruto Financiero)
45 - GASTOS DE OPERACIÓN
─── MNF (Margen Neto Financiero)
46 - OTRAS PÉRDIDAS OPERACIONALES
─── MDI (Margen de Intermediación)
47 - OTROS GASTOS Y PÉRDIDAS
─── MOP (Margen Operacional)
48 - IMPUESTOS Y PARTICIPACIONES
─── GAI (Ganancia Antes de Impuestos)
─── GDE (Ganancia del Ejercicio)
```

---

## Notas Importantes

1. **Enero siempre inicia nuevo**: El primer mes de cada año tiene el valor directo, no hay desacumulación.

2. **valor_12m requiere 12 meses**: Los primeros 11 meses de cada banco/código tendrán NaN en valor_12m.

3. **Cuentas resumen**: Los códigos MNI, MBF, etc. son creados por este script, no existen en el Excel original.

4. **Valores negativos son válidos**: Las pérdidas aparecen como valores negativos.

---

**Autor**: Dashboard Radar Bancario Ecuador
**Fecha**: 26 de enero de 2026
**Versión**: 1.0
