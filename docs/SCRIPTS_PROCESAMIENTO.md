# Scripts de Procesamiento de Datos

Documentación técnica de los scripts de descarga y procesamiento de datos del Sistema Bancario Ecuatoriano.

---

## Índice

1. [Flujo General](#flujo-general)
2. [descargar.py](#descargarpython)
3. [procesar_balance.py](#procesar_balancepy)
4. [procesar_pyg.py](#procesar_pygpy)
5. [procesar_camel.py](#procesar_camelpy)
6. [crear_master.py](#crear_masterpy)

---

## Flujo General

```
┌─────────────────┐
│  descargar.py   │  Descarga archivos ZIP desde portal web
└────────┬────────┘
         │
         ├─> datos_bancos_diciembre_2025/
         │   └── archivos_excel/
         │       ├── BANCO1/
         │       │   └── BANCO1.xlsx
         │       ├── BANCO2/
         │       └── ...
         ▼
┌─────────────────────────────────────────────────────────┐
│  Scripts de Procesamiento (ejecutar en paralelo)       │
├─────────────────────────────────────────────────────────┤
│  • procesar_balance.py   → balance.parquet             │
│  • procesar_pyg.py       → pyg.parquet                 │
│  • procesar_camel.py     → camel.parquet               │
│  • crear_master.py       → indicadores.parquet, etc.   │
└────────┬────────────────────────────────────────────────┘
         │
         ▼
    master_data/
    ├── balance.parquet
    ├── pyg.parquet
    ├── camel.parquet
    ├── indicadores.parquet
    ├── cartera.parquet
    ├── fuentes_usos.parquet
    └── metadata.json
```

---

## descargar.py

### Propósito
Descarga automática de boletines mensuales desde el portal de la Superintendencia de Bancos del Ecuador usando Selenium para automatización web.

### Ubicación
`scripts/descargar.py`

### Dependencias
```python
- selenium
- webdriver-manager
- requests
- config.py (configuración)
```

### Configuración Requerida

El script requiere un archivo `config.py` en la raíz del proyecto con:

```python
# Año a descargar
ANO_BUSCAR = 2025

# Período descriptivo
PERIODO_DESCARGA = "Diciembre 2025"

# URL del portal
URL_PORTAL = "https://www.superbancos.gob.ec/estadisticas/portalestudios/..."

# Carpeta de destino
CARPETA_BOLETINES_TEXTO = "Boletines Mensuales de Bancos Privados"

# Configuración de Selenium
CHROME_HEADLESS = False  # True para ejecución sin interfaz gráfica
CHROME_MAXIMIZADO = True

# Tiempos de espera (segundos)
TIEMPO_CARGA_PAGINA = 5
TIEMPO_ENTRE_SCROLL = 2
TIEMPO_DESPUES_CLIC = 5
TIEMPO_CARGA_ARCHIVOS = 10

# Descarga
TIMEOUT_DESCARGA = 300
CHUNK_SIZE = 8192
NUMERO_ESPERADO_BANCOS = 24
```

### Flujo de Ejecución

#### 1. Inicialización
```python
# Configurar Chrome con opciones
chrome_options = Options()
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")

# Crear carpeta de salida
download_dir = "datos_bancos_diciembre_2025"
```

#### 2. Navegación Web (Selenium)
```python
# Paso 1: Navegar al portal
driver.get(URL_PORTAL)

# Paso 2: Hacer clic en carpeta "Año 2025"
xpath_ano = f"//*[contains(text(), 'Año {ANO_BUSCAR}')]"
driver.find_element(By.XPATH, xpath_ano).click()

# Paso 3: Hacer clic en carpeta "Boletines"
driver.find_element(By.XPATH, f"//*[contains(text(), '{CARPETA_BOLETINES_TEXTO}')]").click()

# Paso 4: Cargar todos los archivos (scroll dinámico)
for i in range(5):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(TIEMPO_ENTRE_SCROLL)
```

#### 3. Extracción de URLs

Usa JavaScript para extraer los IDs de descarga:

```javascript
var entries = document.querySelectorAll('.entry');
var results = [];

entries.forEach(function(entry) {
    var nameElem = entry.querySelector('.entry_link.entry_action_download');
    if (nameElem && nameElem.textContent.includes('Series Banco') && nameElem.textContent.includes('.zip')) {
        var dataId = entry.getAttribute('data-id');
        if (dataId) {
            results.push({
                nombre: nameElem.textContent.trim(),
                id: dataId
            });
        }
    }
});

return results;
```

Luego construye las URLs de descarga:
```python
download_url = (
    f"https://www.superbancos.gob.ec/estadisticas/portalestudios/wp-admin/admin-ajax.php?"
    f"action=shareonedrive-download&id={archivo['id']}"
    f"&account_id=341c37a6-daa9-4b83-adad-506b00ccb984"
    f"&drive_id=b!Iz-mji9B1EqK1eiAuGWU7x82x3m7uftFja_xK_rSLWY6gLR41EOqTYg222Ho8lwD"
    f"&listtoken=cb2dcac486c20e9c7a63b3bc95e58f46"
)
```

#### 4. Descarga de Archivos ZIP

```python
session = requests.Session()
for archivo in archivos_encontrados:
    response = session.get(archivo['url'], stream=True, timeout=TIMEOUT_DESCARGA)

    with open(filepath, 'wb') as f:
        for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
            if chunk:
                f.write(chunk)
```

#### 5. Descompresión Automática

```python
extracted_dir = os.path.join(download_dir, 'archivos_excel')
os.makedirs(extracted_dir, exist_ok=True)

for zip_filename in archivos_zip:
    banco_name = zip_filename.replace('.zip', '').replace('Series Banco ', '')
    banco_dir = os.path.join(extracted_dir, banco_name)

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(banco_dir)

    # Renombrar archivos Excel con nombre del banco
    for excel_file in excel_files:
        os.rename(old_path, f"{banco_name}.xlsx")
```

### Salida Esperada

```
datos_bancos_diciembre_2025/
├── Series Banco AMAZONAS.zip
├── Series Banco AUSTRO.zip
├── ...
└── archivos_excel/
    ├── AMAZONAS/
    │   └── AMAZONAS.xlsx
    ├── AUSTRO/
    │   └── AUSTRO.xlsx
    └── ...
```

### Manejo de Errores

- **Carpeta no encontrada**: Verifica que el año existe en el portal
- **Archivos faltantes**: Normal si hay fusiones/cierres de bancos
- **Descarga fallida**: Reintenta manualmente o verifica conexión
- **ZIP corrupto**: Descarga individual desde el portal

### Ejemplo de Uso

```bash
# Editar config.py para configurar año y parámetros
python scripts/descargar.py

# Salida esperada:
# [INFO] Encontrados 24 bancos
# [1/24] AMAZONAS ... ✓ (2.3 MB)
# [2/24] AUSTRO ... ✓ (3.1 MB)
# ...
# ✓ TODOS LOS ARCHIVOS SE DESCARGARON CORRECTAMENTE
```

---

## procesar_balance.py

### Propósito
Procesa la hoja **BAL (Balance General)** de todos los bancos y genera un archivo Parquet consolidado.

### Ubicación
`scripts/procesar_balance.py`

### Estructura de la Hoja BAL

```
     A           B              C          D          E       ...
1
2                              BALANCE GENERAL
3
4
5              Fecha:        ene-03     feb-03     mar-03    ...
6
7    1         ACTIVO        12345.6    12456.7    12567.8   ...
8    11        Fondos Disponibles  1234.5  1245.6    ...
9    1101      Caja            123.4      124.5    ...
10   ...       ...             ...        ...       ...
```

### Algoritmo de Procesamiento

#### 1. Extracción de Fechas

```python
# Leer hoja BAL sin header
df_raw = pd.read_excel(ruta_excel, sheet_name='BAL', header=None)

# Extraer fechas de fila 5 (índice 4), desde columna C (índice 2)
fechas_raw = df_raw.iloc[4, 2:].values

# Convertir a datetime
fechas = []
for f in fechas_raw:
    if pd.isna(f):
        continue
    fechas.append(pd.to_datetime(f))
```

#### 2. Cálculo de Nivel Jerárquico

Determina el nivel de la cuenta según la cantidad de dígitos:

```python
def calcular_nivel(codigo: str) -> int:
    """
    Nivel 1: 1 dígito (Activo, Pasivo, Patrimonio)
    Nivel 2: 2 dígitos (Fondos Disponibles, Cartera)
    Nivel 3: 4 dígitos (Caja, Bancos)
    Nivel 4: 6 dígitos (Detalle específico)
    Nivel 5: >6 dígitos (Máximo detalle)
    """
    codigo_limpio = str(codigo).strip().replace('.', '').replace(' ', '')

    if not codigo_limpio.isdigit():
        return 0

    longitud = len(codigo_limpio)

    if longitud <= 1:
        return 1
    elif longitud <= 2:
        return 2
    elif longitud <= 4:
        return 3
    elif longitud <= 6:
        return 4
    else:
        return 5
```

Ejemplos:
- `'1'` → Nivel 1 (ACTIVO)
- `'11'` → Nivel 2 (FONDOS DISPONIBLES)
- `'1101'` → Nivel 3 (CAJA)
- `'110105'` → Nivel 4 (CAJA - MONEDA NACIONAL)

#### 3. Transformación a Formato Largo

```python
# Extraer datos
codigos = df_datos.iloc[:, 0].values
cuentas = df_datos.iloc[:, 1].values
valores = df_datos.iloc[:, 2:2+len(fechas)].values

# Crear registros
registros = []
for i in range(len(codigos)):
    for j, fecha in enumerate(fechas):
        valor = valores[i, j]

        registros.append({
            'banco': nombre_banco,
            'fecha': fecha,
            'codigo': str(codigo).strip(),
            'cuenta': str(cuenta).strip(),
            'valor': float(valor),
            'nivel': calcular_nivel(codigo)
        })

df_resultado = pd.DataFrame(registros)
```

#### 4. Optimización de Tipos

```python
# Reducir uso de memoria
df_consolidado['banco'] = df_consolidado['banco'].astype('category')
df_consolidado['codigo'] = df_consolidado['codigo'].astype(str)
df_consolidado['cuenta'] = df_consolidado['cuenta'].astype(str)
df_consolidado['nivel'] = df_consolidado['nivel'].astype('int8')  # 0-5
```

### Salida Generada

**Archivo**: `master_data/balance.parquet`

**Estructura**:
```python
Columns: ['banco', 'fecha', 'codigo', 'cuenta', 'valor', 'nivel']

Ejemplo:
   banco        fecha  codigo    cuenta                      valor  nivel
0  PICHINCHA    2003-01  1        ACTIVO                    12345.6   1
1  PICHINCHA    2003-01  11       FONDOS DISPONIBLES        1234.5    2
2  PICHINCHA    2003-01  1101     CAJA                      123.4     3
```

**Estadísticas**:
- Registros: ~8,300,000+
- Tamaño: ~80 MB
- Bancos: 24
- Fechas: 276 (ene-2003 a dic-2025)
- Cuentas únicas: ~200

### Metadata Generada

```json
{
  "ultima_actualizacion": "2026-01-26T15:30:00",
  "bancos_procesados": ["PICHINCHA", "GUAYAQUIL", ...],
  "bancos_error": [],
  "total_bancos": 24,
  "total_registros": 8300000,
  "fecha_min": "2003-01-01",
  "fecha_max": "2025-12-01",
  "hojas_procesadas": ["BAL"]
}
```

### Ejemplo de Uso

```bash
python scripts/procesar_balance.py

# Salida:
# ======================================================================
# PROCESADOR DE BALANCE GENERAL (HOJA BAL)
# ======================================================================
#
# [INFO] Encontrados 24 bancos
#
# [ 1/24] PICHINCHA... [OK] 345,600 registros
# [ 2/24] GUAYAQUIL... [OK] 345,600 registros
# ...
#
# [OK] Guardado: master_data/balance.parquet
#     - Registros: 8,294,400
#     - Tamaño: 79.84 MB
#     - Bancos: 24
#     - Fechas: 276
#     - Cuentas únicas: 198
```

---

## procesar_pyg.py

### Propósito
Procesa la hoja **PYG (Pérdidas y Ganancias)** con lógica especial de **desacumulación** y **suma móvil de 12 meses**.

### Ubicación
`scripts/procesar_pyg.py`

### Problema de los Datos Acumulados

Los datos de PYG en los archivos Excel están **acumulados dentro de cada año**:

```
Mes       Ingreso Mensual    Valor en Excel (acumulado)
Enero          100                   100
Febrero         80                   180  (100 + 80)
Marzo          120                   300  (100 + 80 + 120)
...
Diciembre       90                  1200  (suma de todos los meses)
```

Para análisis mensual, necesitamos **desacumular** estos valores.

### Algoritmo de Desacumulación

```python
def desacumular_valores(df: pd.DataFrame) -> pd.DataFrame:
    """
    Desacumula valores mensuales.

    Lógica:
    - Enero: valor_mes = valor_acumulado (primer mes)
    - Feb-Dic: valor_mes = valor_acumulado - valor_acumulado_anterior
    """
    df = df.sort_values(['banco', 'codigo', 'fecha']).copy()
    df['ano'] = df['fecha'].dt.year
    df['mes'] = df['fecha'].dt.month

    # Valor del mes anterior (mismo banco, código, año)
    df['valor_anterior'] = df.groupby(['banco', 'codigo', 'ano'])['valor_acumulado'].shift(1)

    # Desacumular
    df['valor_mes'] = np.where(
        (df['mes'] == 1) | (df['valor_anterior'].isna()),
        df['valor_acumulado'],  # Enero o sin anterior
        df['valor_acumulado'] - df['valor_anterior']  # Resto de meses
    )

    return df
```

**Ejemplo**:
```python
# Datos originales (acumulados)
banco      fecha       codigo  valor_acumulado  →  valor_mes
PICHINCHA  2025-01-01  MOP     100                  100  (enero)
PICHINCHA  2025-02-01  MOP     180                   80  (180-100)
PICHINCHA  2025-03-01  MOP     300                  120  (300-180)
```

### Suma Móvil de 12 Meses

Para comparar cualquier mes con cualquier otro (evitar estacionalidad), calculamos una suma móvil de 12 meses:

```python
def calcular_suma_movil_12m(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula suma móvil de 12 meses.
    Permite comparar cualquier mes con períodos anteriores.
    """
    df = df.sort_values(['banco', 'codigo', 'fecha']).copy()

    # Rolling sum de 12 meses por banco/código
    df['valor_12m'] = df.groupby(['banco', 'codigo'])['valor_mes'].transform(
        lambda x: x.rolling(window=12, min_periods=12).sum()
    )

    return df
```

**Ventaja**: El valor de diciembre (acumulado anual) es comparable con el valor_12m de cualquier otro mes.

```python
# Ejemplo: Ganancia anual
Mes          valor_mes    valor_12m (últimos 12 meses)
2024-12-01      90          1200  (suma anual)
2025-01-01     100          1210  (últimos 12 meses desde ene-2025)
2025-06-01      85          1180  (últimos 12 meses desde jun-2025)
```

### Códigos de Cuentas Resumen

Algunas filas tienen código `--` en lugar de número. Se les asignan códigos personalizados:

```python
CODIGOS_RESUMEN = {
    'MARGEN NETO DE INTERESES': 'MNI',
    'MARGEN BRUTO FINANCIERO': 'MBF',
    'MARGEN NETO FINANCIERO': 'MNF',
    'MARGEN DE INTERMEDIACION': 'MDI',
    'MARGEN OPERACIONAL': 'MOP',
    'GANANCIA O PERDIDA ANTES DE IMPUESTOS': 'GAI',
    'GANANCIA O PERDIDA DEL EJERCICIO': 'GDE',
}

def obtener_codigo_resumen(nombre: str) -> str:
    """Busca coincidencia en el nombre de la cuenta."""
    nombre_limpio = limpiar_nombre_cuenta(nombre)
    for clave, codigo in CODIGOS_RESUMEN.items():
        if clave in nombre_limpio:
            return codigo
    return None
```

### Salida Generada

**Archivo**: `master_data/pyg.parquet`

**Estructura**:
```python
Columns: ['banco', 'fecha', 'codigo', 'cuenta', 'valor_acumulado', 'valor_mes', 'valor_12m']

Ejemplo:
   banco      fecha     codigo  cuenta                valor_acumulado  valor_mes  valor_12m
0  PICHINCHA  2025-01  MOP     MARGEN OPERACIONAL      100.0          100.0      1200.5
1  PICHINCHA  2025-02  MOP     MARGEN OPERACIONAL      180.0           80.0      1180.5
```

**Estadísticas**:
- Registros: 769,792
- Tamaño: ~9.4 MB
- Bancos: 24
- Fechas: 276
- Cuentas únicas: 128
- Registros con valor_12m: 95.6%

### Ejemplo de Uso

```bash
python scripts/procesar_pyg.py

# Salida:
# ============================================================
# PROCESAMIENTO DE HOJA PYG (PÉRDIDAS Y GANANCIAS)
# ============================================================
#
# Archivos encontrados: 24
#
# [1/24] PICHINCHA
#   -> 32,076 registros
# [2/24] GUAYAQUIL
#   -> 32,076 registros
# ...
#
# Desacumulando valores mensuales...
# Registros después de desacumular: 769,792
#
# Calculando suma móvil de 12 meses...
#
# ========================================
# RESUMEN
# ========================================
# Bancos: 24
# Fechas: 276
# Cuentas únicas: 128
# Registros totales: 769,792
#
# Rango de fechas: 2003-01-01 a 2025-12-01
# Registros con valor_12m: 735,820 (95.6%)
#
# [OK] Guardado: master_data/pyg.parquet
#     Tamaño: 9.4 MB
```

---

## procesar_camel.py

### Propósito
Procesa la hoja **INDICAD (Indicadores Financieros)** y extrae los 39 indicadores CAMEL categorizados.

### Ubicación
`scripts/procesar_camel.py`

### Marco CAMEL

**CAMEL** es un sistema de evaluación de bancos:
- **C**: Capital (solvencia)
- **A**: Assets (calidad de activos)
- **M**: Management (gestión)
- **E**: Earnings (rentabilidad)
- **L**: Liquidity (liquidez)

### Indicadores Extraídos (39 total)

#### C - Capital (3 indicadores)
```python
'C': [
    ('SOLVENCIA', 'Solvencia'),
    ('PATRIMONIO TOTAL / ACTIVO TOTAL', 'Patrimonio/Activos'),
    ('APALANCAMIENTO', 'Apalancamiento'),
]
```

#### A - Assets (12 indicadores)
```python
'A': [
    ('MOROSIDAD DE LA CARTERA TOTAL', 'Morosidad Total'),
    ('COBERTURA DE LA CARTERA PROBLEMÁTICA', 'Cobertura'),
    ('CARTERA IMPRODUCTIVA BRUTA / TOTAL CARTERA BRUTA', 'Cartera Improductiva'),
    ('CARTERA IMPRODUCTIVA / PATRIMONIO', 'Improductiva/Patrimonio'),
    # ... 8 más
]
```

#### M - Management (6 indicadores)
```python
'M': [
    ('GASTOS OPERACIONALES / MARGEN FINANCIERO', 'Eficiencia Operativa'),
    ('GASTOS OPERACIONALES / ACTIVO TOTAL PROMEDIO', 'Gastos/Activos'),
    # ... 4 más
]
```

#### E - Earnings (8 indicadores)
```python
'E': [
    ('RESULTADOS DEL EJERCICIO / PATRIMONIO PROMEDIO', 'ROE'),
    ('RESULTADOS DEL EJERCICIO / ACTIVO PROMEDIO', 'ROA'),
    ('MARGEN DE INTERMEDIACIÓN FINANCIERO / PATRIMONIO PROMEDIO', 'Margen/Patrimonio'),
    # ... 5 más
]
```

#### L - Liquidity (2 indicadores)
```python
'L': [
    ('FONDOS DISPONIBLES / TOTAL DEPOSITOS A CORTO PLAZO', 'Liquidez'),
    ('COBERTURA 25 MAYORES DEPOSITANTES', 'Cobertura 25'),
]
```

#### Composicion Cartera (8 categorías)
```python
'Composicion Cartera': [
    ('CARTERA DE CRÉDITO COMERCIAL PRIORITARIO / TOTAL CARTERA', 'Comercial Prioritario'),
    ('CARTERA DE CRÉDITO DE CONSUMO PRIORITARIO / TOTAL CARTERA', 'Consumo Prioritario'),
    ('CARTERA DE CRÉDITO INMOBILIARIO / TOTAL CARTERA', 'Inmobiliario'),
    ('CARTERA DE MICROCRÉDITO / TOTAL CARTERA', 'Microcrédito'),
    # ... 4 más
]
```

### Algoritmo de Extracción

```python
def procesar_banco_camel(ruta_excel: Path, nombre_banco: str) -> pd.DataFrame:
    """Extrae indicadores CAMEL de la hoja INDICAD."""

    # Leer hoja sin header
    df_raw = pd.read_excel(ruta_excel, sheet_name='INDICAD', header=None)

    # Fechas en fila 5, columna C+
    fechas_raw = df_raw.iloc[4, 2:].values
    fechas = [pd.to_datetime(f) for f in fechas_raw if pd.notna(f)]

    # Nombres de indicadores en columna B
    nombres_indicadores = df_raw.iloc[6:, 1].values

    # Valores desde columna C
    valores_matrix = df_raw.iloc[6:, 2:2+len(fechas)].values

    registros = []

    # Buscar cada indicador CAMEL
    for categoria, indicadores in INDICADORES_CAMEL.items():
        for patron_busqueda, nombre_corto in indicadores:
            # Buscar fila que contiene este indicador
            for i, nombre_indicador in enumerate(nombres_indicadores):
                if pd.notna(nombre_indicador) and patron_busqueda in str(nombre_indicador).upper():
                    # Extraer valores de esta fila
                    for j, fecha in enumerate(fechas):
                        valor = valores_matrix[i, j]
                        if pd.notna(valor):
                            registros.append({
                                'banco': nombre_banco,
                                'fecha': fecha,
                                'categoria': categoria,
                                'codigo': patron_busqueda[:20],  # Código abreviado
                                'indicador': nombre_corto,
                                'valor': float(valor)
                            })
                    break

    return pd.DataFrame(registros)
```

### Salida Generada

**Archivo**: `master_data/camel.parquet`

**Estructura**:
```python
Columns: ['banco', 'fecha', 'categoria', 'codigo', 'indicador', 'valor']

Ejemplo:
   banco      fecha      categoria  codigo       indicador    valor
0  PICHINCHA  2025-12   C          SOLVENCIA    Solvencia    14.2
1  PICHINCHA  2025-12   A          MOROSIDAD    Morosidad     2.1
2  PICHINCHA  2025-12   E          ROE          ROE          12.3
```

**Estadísticas**:
- Registros: 233,680
- Tamaño: ~1.5 MB
- Bancos: 24
- Fechas: 276
- Indicadores únicos: 39
- Categorías: 6

### Ejemplo de Uso

```bash
python scripts/procesar_camel.py

# Salida:
# ============================================================
# PROCESAMIENTO DE INDICADORES CAMEL
# ============================================================
#
# [1/24] PICHINCHA
#   -> 10,764 registros
# [2/24] GUAYAQUIL
#   -> 10,764 registros
# ...
#
# ========================================
# RESUMEN
# ========================================
# Bancos: 24
# Fechas: 276
# Indicadores únicos: 39
# Registros totales: 233,680
#
# [OK] Guardado: master_data/camel.parquet
#     Tamaño: 1.5 MB
#
# Categorías CAMEL procesadas:
#   C: 3 indicadores
#   A: 12 indicadores
#   M: 6 indicadores
#   E: 8 indicadores
#   L: 2 indicadores
#   Composicion Cartera: 8 categorías
```

---

## crear_master.py

### Propósito
Consolida las hojas **INDICAD**, **CARTERA** y **FUENTES_USOS** en archivos Parquet.

### Ubicación
`scripts/crear_master.py`

### Hojas Procesadas

#### 1. INDICAD (Indicadores Generales)
- **Contenido**: ~120 indicadores financieros por banco/fecha
- **Salida**: `master_data/indicadores.parquet`
- **Registros**: ~3,800,000+
- **Tamaño**: ~45 MB

#### 2. CARTERA (Estructura de Cartera)
- **Contenido**: Composición de cartera por tipo de crédito
- **Salida**: `master_data/cartera.parquet`
- **Registros**: ~500,000+
- **Tamaño**: ~8 MB

#### 3. FUENTES_USOS (Flujos de Fondos)
- **Contenido**: Fuentes y usos de fondos
- **Salida**: `master_data/fuentes_usos.parquet`
- **Registros**: ~400,000+
- **Tamaño**: ~6 MB

### Ejemplo de Uso

```bash
python scripts/crear_master.py

# Procesa las 3 hojas restantes y genera:
# - indicadores.parquet
# - cartera.parquet
# - fuentes_usos.parquet
```

---

## Comparación de Scripts

| Script | Hoja | Registros | Tamaño | Complejidad | Tiempo |
|--------|------|-----------|--------|-------------|--------|
| `procesar_balance.py` | BAL | 8.3M | 80 MB | Media | 3-5 min |
| `procesar_pyg.py` | PYG | 770K | 9.4 MB | Alta (desacumulación) | 1-2 min |
| `procesar_camel.py` | INDICAD | 234K | 1.5 MB | Media (búsqueda) | 1 min |
| `crear_master.py` | INDICAD, CARTERA, FUENTES_USOS | 4.7M | 59 MB | Baja | 5-8 min |

---

## Optimizaciones Implementadas

### 1. Tipos de Datos Eficientes

```python
# En lugar de:
df['banco'] = df['banco'].astype(str)  # ~300 MB

# Usar:
df['banco'] = df['banco'].astype('category')  # ~50 MB
```

### 2. Formato Parquet con Compresión

```python
df.to_parquet(
    'master_data/balance.parquet',
    index=False,
    compression='snappy'  # Compresión rápida con buena ratio
)
```

### 3. Procesamiento por Lotes

En lugar de cargar todos los bancos en memoria:
```python
dataframes = []
for archivo in archivos:
    df = procesar_banco(archivo)
    dataframes.append(df)

df_final = pd.concat(dataframes, ignore_index=True)
```

### 4. Validación Temprana

```python
# Validar estructura antes de procesar todo
if df_raw.shape[0] < 10 or df_raw.shape[1] < 5:
    print(f"[WARN] Archivo muy pequeño: {archivo.name}")
    return pd.DataFrame()
```

---

## Solución de Problemas Comunes

### Error: "FileNotFoundError: datos_bancos_diciembre_2025"

**Causa**: No se ejecutó `descargar.py` primero.

**Solución**:
```bash
python scripts/descargar.py
```

### Error: "KeyError: 'BAL'"

**Causa**: El archivo Excel no tiene la hoja BAL.

**Solución**: Verificar que el archivo descargado es correcto. Algunos bancos pueden tener formato diferente.

### Warning: "Sin fechas válidas"

**Causa**: La fila 5 del Excel no contiene fechas.

**Solución**: Verificar manualmente el archivo Excel. Puede estar corrupto o tener formato diferente.

### Error: "MemoryError"

**Causa**: No hay suficiente RAM para procesar todos los datos.

**Solución**: Procesar bancos en lotes más pequeños o aumentar memoria swap.

### Valores `valor_12m` = NaN

**Causa**: Normal para los primeros 11 meses de cada banco/código.

**Explicación**: La suma móvil de 12 meses requiere al menos 12 valores previos.

---

## Mejores Prácticas

### 1. Ejecutar en Orden

```bash
# Orden correcto:
python scripts/descargar.py
python scripts/procesar_balance.py
python scripts/procesar_pyg.py
python scripts/procesar_camel.py
python scripts/crear_master.py
```

### 2. Verificar Salidas

Después de cada script, verificar:
```bash
ls -lh master_data/
# Debe mostrar archivos .parquet con tamaños esperados
```

### 3. Backup de Datos Crudos

```bash
# Respaldar archivos descargados
cp -r datos_bancos_diciembre_2025 backup/
```

### 4. Validar con Dashboard

```bash
# Verificar que el dashboard carga correctamente
streamlit run app.py
```

---

## Referencias

- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [Parquet Format](https://parquet.apache.org/docs/)
- [Selenium WebDriver](https://www.selenium.dev/documentation/webdriver/)
- [Superintendencia de Bancos del Ecuador](https://www.superbancos.gob.ec/)

---

**Última actualización**: 26 de enero de 2026
