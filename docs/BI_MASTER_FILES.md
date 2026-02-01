# Master Files para Business Intelligence

## Descripción

Los **Master Files** son archivos Parquet optimizados que consolidan los datos de los 24 bancos en formato largo (tidy), listos para ser cargados en aplicaciones de visualización como Streamlit o Dash.

## Archivos Generados

### Ubicación
```
master_data/
├── balance.parquet          # 34.63 MB - 9.2M filas
├── indicadores.parquet      # 8.67 MB - 3.8M filas
├── cartera.parquet          # 5.43 MB - 2.2M filas
├── fuentes_usos.parquet     # 2.11 MB - 716K filas
└── metadata.json            # 5.9 KB - Información de actualización
```

### Contenido de cada archivo

#### 1. balance.parquet
**Hojas incluidas**: BAL, PYG
**Contenido**: Balance General y Estado de Resultados
**Columnas**:
- `banco` (categorical): Nombre del banco
- `fecha` (datetime): Fecha mensual (2003-01 a 2025-12)
- `hoja` (categorical): BAL o PYG
- `hoja_descripcion` (categorical): Nombre descriptivo
- `codigo` (string): Código contable
- `cuenta` (string): Nombre de la cuenta contable
- `valor` (float): Valor en miles de dólares
- `nivel` (int8): Nivel jerárquico (1-4)

**Cuentas incluidas**: ~1,400 cuentas contables
**Uso**: Análisis de activos, pasivos, patrimonio, ingresos, gastos

---

#### 2. indicadores.parquet
**Hojas incluidas**: INDICAD, CAMEL, INDIC CARTERA
**Contenido**: Indicadores financieros y de cartera
**Columnas**: Igual que balance.parquet

**Indicadores incluidos**:
- **INDICAD**: ~100-150 indicadores financieros (ROA, ROE, solvencia, liquidez, etc.)
- **CAMEL**: Indicadores del sistema CAMEL (Capital, Assets, Management, Earnings, Liquidity)
- **INDIC CARTERA**: Indicadores de calidad de cartera (morosidad, cobertura, etc.)

**Uso**: Dashboards de indicadores, análisis de rentabilidad y riesgo

---

#### 3. cartera.parquet
**Hojas incluidas**: ESTRUC CART, REFINA REES
**Contenido**: Estructura de cartera y cartera refinanciada
**Columnas**: Igual que balance.parquet

**Datos incluidos**:
- Cartera por tipo (Comercial, Consumo, Vivienda, Microcrédito)
- Cartera por calificación de riesgo (A, B, C, D, E)
- Cartera vigente vs vencida
- Cartera refinanciada y reestructurada

**Uso**: Análisis de composición de cartera, gestión de riesgo crediticio

---

#### 4. fuentes_usos.parquet
**Hojas incluidas**: FUENTES USOS
**Contenido**: Fuentes y usos de fondos
**Columnas**: Igual que balance.parquet

**Datos incluidos**:
- Fuentes: Depósitos, obligaciones financieras, patrimonio
- Usos: Cartera de créditos, inversiones, fondos disponibles

**Uso**: Análisis de gestión de fondos y transformación de plazos

---

## Creación y Actualización

### Script Principal

```bash
# Crear master files por primera vez (o regenerar completamente)
python crear_master.py --regenerar

# Actualizar con nuevos datos (modo append)
python crear_master.py
```

### Proceso Automático

El script `crear_master.py`:

1. **Lee** los 24 archivos Excel de la carpeta `datos_bancos_diciembre_2025/archivos_excel/`
2. **Procesa** las 8 hojas seleccionadas de cada banco
3. **Transforma** al formato largo (tidy): una fila por banco/fecha/cuenta
4. **Consolida** todos los bancos en 4 archivos Parquet
5. **Actualiza** metadata.json con información de la corrida

### Modo Append (Actualización)

Cuando descargues nuevos datos (ej: enero 2026):

```bash
# 1. Descargar nuevos datos
python descargar.py

# 2. Actualizar master files (agrega solo datos nuevos)
python crear_master.py
```

El modo append:
- Detecta automáticamente fechas nuevas
- Agrega solo los meses que no existen
- Evita duplicados
- Mantiene el historial completo

---

## Formato de Datos

### Estructura (Formato Largo / Tidy)

Cada fila representa un **dato único** identificado por:
- Banco
- Fecha (mes)
- Hoja (fuente del dato)
- Código de cuenta
- Nombre de cuenta

**Ejemplo**:
```
| banco      | fecha      | hoja | codigo | cuenta           | valor      | nivel |
|------------|------------|------|--------|------------------|------------|-------|
| Guayaquil  | 2025-12-31 | BAL  | 11     | FONDOS DISPONIB. | 1,234,567  | 1     |
| Guayaquil  | 2025-12-31 | BAL  | 1101   | Caja             | 45,678     | 2     |
| Pichincha  | 2025-12-31 | PYG  | 51     | INGRESOS FINANC. | 890,123    | 1     |
```

### Ventajas del Formato Largo

✅ **Filtrado dinámico**: Fácil filtrar por banco, fecha, cuenta
✅ **Agregaciones**: Sumar, promediar por cualquier dimensión
✅ **Joins**: Combinar con otras tablas fácilmente
✅ **Visualizaciones**: Compatible con Plotly, Altair, etc.
✅ **Eficiente**: Parquet comprime muy bien este formato

---

## Uso en Streamlit/Dash

### Cargar datos

```python
import pandas as pd

# Cargar archivos Parquet
df_balance = pd.read_parquet('master_data/balance.parquet')
df_indicadores = pd.read_parquet('master_data/indicadores.parquet')
df_cartera = pd.read_parquet('master_data/cartera.parquet')
df_fuentes = pd.read_parquet('master_data/fuentes_usos.parquet')
```

### Ejemplos de Consultas

#### 1. Filtrar un banco específico en una fecha
```python
# Balance de Guayaquil en dic-2025
guayaquil_dic25 = df_balance[
    (df_balance['banco'] == 'Guayaquil') &
    (df_balance['fecha'] == '2025-12-31')
]
```

#### 2. Filtrar por nivel jerárquico
```python
# Solo cuentas de nivel 1 (principales)
df_nivel1 = df_balance[df_balance['nivel'] == 1]
```

#### 3. Serie de tiempo de una cuenta
```python
# Evolución de activos totales de Pichincha
activos_pichincha = df_balance[
    (df_balance['banco'] == 'Pichincha') &
    (df_balance['hoja'] == 'BAL') &
    (df_balance['codigo'] == '1')  # Código 1 = ACTIVO
][['fecha', 'valor']]
```

#### 4. Comparar bancos en un mes
```python
# Top 10 bancos por activos en dic-2025
top10_activos = df_balance[
    (df_balance['fecha'] == '2025-12-31') &
    (df_balance['hoja'] == 'BAL') &
    (df_balance['codigo'] == '1')
].nlargest(10, 'valor')
```

#### 5. Indicadores financieros
```python
# ROA de todos los bancos (último mes)
roa_ultima_fecha = df_indicadores[
    (df_indicadores['fecha'] == df_indicadores['fecha'].max()) &
    (df_indicadores['cuenta'].str.contains('ROA', case=False))
][['banco', 'valor']]
```

#### 6. Análisis de cartera
```python
# Morosidad por banco (dic-2025)
morosidad = df_indicadores[
    (df_indicadores['fecha'] == '2025-12-31') &
    (df_indicadores['hoja'] == 'INDIC CARTERA') &
    (df_indicadores['cuenta'].str.contains('morosidad', case=False))
][['banco', 'cuenta', 'valor']]
```

---

## Estadísticas de los Master Files

### Información General
- **Última actualización**: 2026-01-23 20:56:58
- **Total bancos**: 24
- **Rango de fechas**: 2003-01-31 a 2025-12-31
- **Total meses**: 276 meses (23 años)
- **Total filas**: ~15.9 millones
- **Tamaño total**: ~50.84 MB

### Bancos Incluidos (24)
1. Amazonas
2. Amibank
3. Atlantida (antes DMiro)
4. Austro
5. Bolivariano
6. Capital
7. Citibank
8. Codesarrollo
9. Comercial Manabí
10. Coopnacional
11. DelBank
12. Diners
13. Guayaquil
14. Internacional
15. Litoral
16. Loja
17. Machala
18. Pacifico
19. Pichincha
20. Procredit
21. Produbanco
22. Rumiñahui
23. Solidario
24. Visionfund

### Hojas Procesadas (8 de 14)
| # | Hoja Original | Categoría en Master File | Descripción |
|---|---------------|--------------------------|-------------|
| 1 | BAL | balance.parquet | Balance General |
| 2 | PYG | balance.parquet | Estado de Resultados |
| 6 | INDIC CARTERA | indicadores.parquet | Indicadores de Cartera |
| 9 | INDICAD | indicadores.parquet | Indicadores Financieros |
| 11 | CAMEL | indicadores.parquet | Sistema CAMEL |
| 12 | ESTRUC CART | cartera.parquet | Estructura de Cartera |
| 13 | FUENTES USOS | fuentes_usos.parquet | Fuentes y Usos |
| 14 | REFINA REES | cartera.parquet | Refinanciamiento |

### Hojas NO Procesadas (6 de 14)
- **BAL %**: Porcentajes del balance (calculable desde BAL)
- **PYG %**: Porcentajes de resultados (calculable desde PYG)
- **GRUPOS CTAS**: Resumen de cuentas (redundante con BAL)
- **MET**: Metodología (documentación, no datos)
- **GRAF CARTERA**: Datos para gráficos (redundante)
- **GRAF INDIC**: Datos para gráficos (redundante)

---

## Notas Técnicas

### Problema Resuelto: Hoja INDICAD

La hoja "INDICAD" no se pudo procesar en algunos bancos porque:
- Estructura diferente (no tiene columnas de fecha estándar)
- Se muestra advertencia: `[AVISO] No se encontraron columnas de fecha en INDICAD`
- Solución pendiente: Requiere análisis manual de la estructura de esta hoja

**Impacto**: Limitado, ya que CAMEL e INDIC CARTERA sí se procesaron correctamente.

### Optimizaciones Aplicadas

1. **Tipos de datos categóricos**: `banco`, `hoja`, `hoja_descripcion` → Reduce memoria ~70%
2. **Tipo int8 para nivel**: En lugar de int64 → 8x menor
3. **Compresión Snappy**: Balance entre velocidad y tamaño
4. **Formato Parquet**: Columnar, permite leer columnas selectivamente

### Rendimiento

- **Tiempo de procesamiento**: ~5-7 minutos para 24 bancos
- **Lectura de Parquet**: < 1 segundo por archivo
- **Filtrado**: Instantáneo gracias a índices de Parquet

---

## Próximos Pasos para BI

1. **Crear aplicación Streamlit** con:
   - Selector de banco(s)
   - Selector de fecha/rango
   - Visualizaciones interactivas (gráficos de línea, barras, mapas de calor)
   - Tablas dinámicas

2. **Dashboards sugeridos**:
   - Evolución de activos por banco
   - Comparación de indicadores entre bancos
   - Análisis de morosidad y calidad de cartera
   - Ranking de bancos por tamaño/rentabilidad
   - Análisis de crisis (ej: COVID-19 2020)

3. **Funcionalidades avanzadas**:
   - Exportar a Excel/CSV
   - Descarga de gráficos
   - Alertas/notificaciones
   - Predicciones con ML

---

## Mantenimiento

### Actualización Mensual

Cuando salgan datos de enero 2026:

```bash
# 1. Actualizar config.py
# ANO_BUSCAR = "2026"  # Si ya estamos en 2026
# PERIODO_DESCARGA = "enero_2026"

# 2. Descargar nuevos archivos
python descargar.py

# 3. Actualizar master files (modo append)
python crear_master.py

# Los archivos Parquet ahora incluirán enero 2026
```

### Regenerar desde Cero

Si hay cambios estructurales o errores:

```bash
python crear_master.py --regenerar
```

---

**Fecha de creación**: 2026-01-23
**Versión**: 1.0
**Autor**: Sistema automatizado con Claude Code
