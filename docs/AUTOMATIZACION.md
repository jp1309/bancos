# Automatización de Actualización de Datos

Este documento describe el sistema de actualización automática de datos del Radar Bancario Ecuador.

## Resumen

El sistema descarga automáticamente los datos de la Superintendencia de Bancos del Ecuador cada mes, los procesa y actualiza el dashboard en Streamlit Cloud.

## Flujo de Actualización

```
┌─────────────────────────────────────────────────────────────────┐
│                    PROCESO AUTOMÁTICO MENSUAL                    │
└─────────────────────────────────────────────────────────────────┘

        Día 10 del mes (8:00 AM hora Ecuador)
                         │
                         ▼
              ┌─────────────────────┐
              │ GitHub Actions      │
              │ inicia workflow     │
              └──────────┬──────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │ ¿Ya están los datos │
              │ del mes anterior?   │
              └──────────┬──────────┘
                         │
            ┌────────────┴────────────┐
            │                         │
            ▼ NO                      ▼ SÍ
   ┌─────────────────┐       ┌─────────────────┐
   │ Descargar datos │       │ Fin (no hacer   │
   │ de la SBS       │       │ nada)           │
   └────────┬────────┘       └─────────────────┘
            │
            ▼
   ┌─────────────────┐
   │ Procesar datos: │
   │ • Balance       │
   │ • PyG           │
   │ • CAMEL         │
   └────────┬────────┘
            │
            ▼
   ┌─────────────────┐
   │ Guardar archivos│
   │ .parquet        │
   └────────┬────────┘
            │
            ▼
   ┌─────────────────┐
   │ Commit y push   │
   │ automático      │
   └────────┬────────┘
            │
            ▼
   ┌─────────────────┐
   │ Streamlit Cloud │
   │ detecta cambios │
   │ y actualiza     │
   └─────────────────┘
```

## Archivos del Sistema

### 1. Workflow de GitHub Actions
**Archivo:** `.github/workflows/actualizar-datos.yml`

- **Cuándo se ejecuta:** Del día 10 al 15 de cada mes a las 8:00 AM (hora Ecuador)
- **Por qué del 10 al 15:** La Superintendencia publica los datos el día 10, pero a veces hay retrasos
- **Ejecución manual:** También se puede ejecutar manualmente desde GitHub Actions

### 2. Configuración
**Archivo:** `scripts/config.py`

Configura automáticamente:
- El periodo a descargar (mes anterior)
- La URL del portal de la Superintendencia
- Modo headless de Chrome (sin ventana visible)
- Tiempos de espera para scraping

### 3. Script Maestro
**Archivo:** `scripts/actualizar_datos.py`

Orquesta todo el proceso:
1. Verifica si ya se descargaron los datos del mes
2. Ejecuta `descargar.py` para obtener los datos
3. Ejecuta `procesar_balance.py`, `procesar_pyg.py`, `procesar_camel.py`
4. Verifica que los archivos se generaron correctamente
5. Guarda el estado de la actualización

### 4. Scripts de Descarga y Procesamiento

| Script | Función |
|--------|---------|
| `scripts/descargar.py` | Descarga los archivos ZIP de la Superintendencia usando Selenium |
| `scripts/descomprimir_zips.py` | Descomprime los archivos ZIP descargados |
| `scripts/procesar_balance.py` | Procesa la hoja BAL (Balance General) → `balance.parquet` |
| `scripts/procesar_pyg.py` | Procesa la hoja PYG (Pérdidas y Ganancias) → `pyg.parquet` |
| `scripts/procesar_camel.py` | Calcula indicadores CAMEL → `camel.parquet` |

## Archivos de Datos

Los datos procesados se almacenan en la carpeta `master_data/`:

| Archivo | Descripción | Tamaño aprox. |
|---------|-------------|---------------|
| `balance.parquet` | Balance General de todos los bancos (2003-presente) | ~18 MB |
| `pyg.parquet` | Pérdidas y Ganancias (2003-presente) | ~10 MB |
| `camel.parquet` | Indicadores CAMEL calculados | ~1.6 MB |
| `metadata.json` | Información de la última actualización | <1 KB |
| `update_status.json` | Estado del proceso de actualización | <1 KB |

## Calendario de Ejecución

```
Enero    → El día 10 se descargan datos de Diciembre del año anterior
Febrero  → El día 10 se descargan datos de Enero
Marzo    → El día 10 se descargan datos de Febrero
...
Diciembre → El día 10 se descargan datos de Noviembre
```

## Manejo de Errores

### Si los datos no están disponibles el día 10:
- El workflow falla pero registra el intento
- Se vuelve a ejecutar automáticamente el día 11, 12, 13, 14 o 15
- Una vez que los datos están disponibles, se descargan y procesan

### Si el procesamiento falla:
- El estado queda como "fallido" en `update_status.json`
- Se puede revisar el log en GitHub Actions
- Se puede ejecutar manualmente una vez corregido el problema

## Ejecución Manual

### Desde GitHub (recomendado):
1. Ir a https://github.com/jp1309/bancos/actions
2. Seleccionar "Actualizar Datos Bancarios"
3. Clic en "Run workflow"
4. Clic en el botón verde "Run workflow"

### Desde línea de comandos (local):
```bash
cd c:\Users\HP\OneDrive\JpE\Github\bancos
python scripts/actualizar_datos.py
```

## Dependencias

### Para Streamlit (producción):
Archivo: `requirements.txt`
```
streamlit>=1.28.0
pandas>=2.0.0
numpy>=1.24.0
pyarrow>=12.0.0
plotly>=5.14.0
kaleido
```

### Para Scraping (GitHub Actions):
Archivo: `requirements-scraping.txt`
```
selenium>=4.15.0
webdriver-manager>=4.0.1
requests>=2.31.0
pandas>=2.0.0
numpy>=1.24.0
pyarrow>=12.0.0
openpyxl>=3.1.0
```

## Monitoreo

### Ver estado de las ejecuciones:
- GitHub Actions: https://github.com/jp1309/bancos/actions

### Ver última actualización:
- En el dashboard: Aparece la fecha de última actualización
- En el archivo: `master_data/update_status.json`

## Fuente de Datos

**Portal:** Superintendencia de Bancos del Ecuador
**URL:** https://www.superbancos.gob.ec/estadisticas/portalestudios/boletines-financieros-mensuales/

Los datos son públicos y no requieren autenticación.

## Notas Importantes

1. **Los archivos .parquet están en el repositorio:** Esto permite que Streamlit Cloud funcione sin necesidad de ejecutar el scraping cada vez.

2. **El workflow usa Chrome headless:** No necesita interfaz gráfica para funcionar en GitHub Actions.

3. **Los datos temporales se eliminan:** Después de procesar, se eliminan los archivos ZIP y Excel descargados para no ocupar espacio en el repositorio.

4. **Streamlit Cloud se actualiza automáticamente:** Cuando se hace push de nuevos archivos parquet, Streamlit Cloud detecta los cambios y reinicia la aplicación.
