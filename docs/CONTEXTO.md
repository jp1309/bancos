# Contexto Persistente - Radar Bancario Ecuador

Este archivo es la fuente de verdad para recuperar contexto cuando el asistente pierda memoria.
Si estas leyendo esto, **DEBES actualizar este archivo** con cualquier cambio relevante antes de terminar la tarea.

## Instrucciones para el asistente
- Siempre leer `docs/CONTEXTO.md` al inicio de una nueva sesion.
- Actualizar este archivo al finalizar cambios.
- Si se detectan errores cometidos previamente, registrarlos aqui.

## Resumen del proyecto (actual)
- App Streamlit para analisis del sistema bancario ecuatoriano (2003-2025).
- Entry point: `Inicio.py`.
- Modulos activos en `pages/`:
  - `1_Panorama.py`
  - `2_Balance_General.py`
  - `3_Perdidas_y_Ganancias.py`
  - `4_CAMEL.py`
- Modulo de calidad archivado: `archived_pages/0_Calidad_old.py`.

## Pipeline de datos
1. `scripts/descargar.py`: descarga ZIPs y descomprime a `datos_bancos_*/archivos_excel/`.
2. `scripts/procesar_balance.py` -> `master_data/balance.parquet`.
3. `scripts/procesar_pyg.py` -> `master_data/pyg.parquet`.
4. `scripts/procesar_camel.py` -> `master_data/camel.parquet`.
5. Orquestador opcional: `scripts/actualizar_datos.py`.

## Datos principales
- `master_data/balance.parquet`
- `master_data/pyg.parquet`
- `master_data/camel.parquet`
- `master_data/metadata.json`
- `master_data/update_status.json`

## Documentacion clave
- `README.md`
- `RESUMEN_PROYECTO.md`
- `docs/PIPELINE.md`
- `docs/ESTRUCTURA_FINAL.md`

## Errores previos a evitar
- Asumir que el entrypoint es `app.py` (es `Inicio.py`).
- Documentar modulos inexistentes en `pages/6_*.py` o `pages/7_*.py`.
- Referenciar `crear_master.py` como activo (fue eliminado).
- Listar `indicadores.parquet`, `cartera.parquet`, `fuentes_usos.parquet` como salidas actuales.
- Decir que el modulo de Calidad esta activo cuando esta archivado.

## Ultima actualizacion
- Fecha: 2026-02-05
- Motivo: Creacion de contexto persistente y alineacion documental.
