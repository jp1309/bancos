# Pipeline de Datos - Radar Bancario Ecuador

Este documento resume el flujo real de datos desde la descarga hasta el dashboard.

## Flujo General

```
Portal Superintendencia de Bancos
        |
        v
scripts/descargar.py
  - Selenium + requests
  - Descarga ZIPs
  - Descomprime a datos_bancos_*/archivos_excel/
        |
        v
scripts/procesar_balance.py  -> master_data/balance.parquet
scripts/procesar_pyg.py      -> master_data/pyg.parquet
scripts/procesar_camel.py    -> master_data/camel.parquet
        |
        v
utils/data_loader.py
  - Limpieza + cache (st.cache_data)
        |
        v
Streamlit App
Inicio.py + pages/*.py
```

## Archivos de Salida Clave

- `master_data/balance.parquet`
- `master_data/pyg.parquet`
- `master_data/camel.parquet`
- `master_data/metadata.json`
- `master_data/update_status.json`

## Script Orquestador (opcional)

El script `scripts/actualizar_datos.py` ejecuta la descarga, el procesamiento y la verificacion
de archivos en secuencia.

