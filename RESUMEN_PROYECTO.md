# Ficha del proyecto

## Propósito

Radar Bancario Ecuador transforma boletines mensuales por entidad de la Superintendencia de Bancos en tres datasets Parquet y una aplicación Streamlit para análisis histórico y comparativo.

## Estado verificado

| Elemento | Estado |
|---|---|
| Aplicación | [Pública en Streamlit](https://jp1309-bancos.streamlit.app/) |
| Rama de producción | `main` |
| Entry point | `Inicio.py` |
| Corte publicado | 31 de julio de 2026 |
| Cobertura último mes | 23 bancos en Balance, PyG y CAMEL |
| Historia | enero de 2003-julio de 2026 |
| Automatización | GitHub Actions, revisión diaria del 6 al 20 |
| Licencia | MIT para el software |

## Productos de datos

| Archivo | Filas | Tamaño aproximado | Uso |
|---|---:|---:|---|
| `master_data/balance.parquet` | 8.183.806 | 19,66 MB | Balance y Panorama |
| `master_data/pyg.parquet` | 758.528 | 9,59 MB | Pérdidas y Ganancias |
| `master_data/camel.parquet` | 230.999 | 1,56 MB | Indicadores CAMEL |

Las cifras corresponden a la fotografía validada el 14 de agosto de 2026 y deben leerse junto con `master_data/metadata.json`.

## Componentes

- **Descarga:** Selenium descubre los enlaces vigentes; Requests usa reintentos y Chrome actúa como transporte seguro alternativo ante cadenas TLS incompletas.
- **Inspección de fuente:** valida 23 ZIP, un XLSX por entidad, hojas BAL/PYG/CAMEL y una fecha uniforme.
- **ETL:** procesadores independientes generan los tres Parquet.
- **Puerta de calidad:** valida esquema, fechas, continuidad, bancos, duplicados, metadata e historia.
- **Publicación:** GitHub Actions hace commit solo cuando existe un avance real.
- **Consumo:** Streamlit carga Parquet versionados desde el repositorio.

## Principios operativos

1. Un HTTP 200 o un ZIP válido no demuestra que exista un mes nuevo; se inspecciona la fecha interna.
2. La ausencia de avance devuelve código `2` y no publica nada.
3. Los tres datasets constituyen una sola unidad de publicación.
4. Un fallo de ETL o validación restaura el estado anterior.
5. La portada y los módulos leen fechas y bancos desde los datos, no desde constantes visuales.

## Documentos principales

- [README](README.md)
- [Índice técnico](docs/README.md)
- [Automatización](docs/AUTOMATIZACION.md)
- [Operación y recuperación](docs/OPERACION_Y_RECUPERACION.md)
- [Diccionario de datos](docs/DICCIONARIO_DATOS.md)
- [Arquitectura](docs/ARQUITECTURA.md)
