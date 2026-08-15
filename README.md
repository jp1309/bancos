# Radar Bancario Ecuador

[![Actualizar Datos Bancarios](https://github.com/jp1309/bancos/actions/workflows/actualizar-datos.yml/badge.svg)](https://github.com/jp1309/bancos/actions/workflows/actualizar-datos.yml)

Dashboard público en Streamlit para explorar la evolución del sistema bancario privado ecuatoriano con datos oficiales de la Superintendencia de Bancos.

- **Aplicación:** [jp1309-bancos.streamlit.app](https://jp1309-bancos.streamlit.app/)
- **Fuente:** [Boletines de Series por Entidad](https://www.superbancos.gob.ec/estadisticas/portalestudios/bancos-2/)
- **Autor:** Juan Pablo Erráez T.
- **Licencia del código:** [MIT](LICENSE)

## Estado de los datos

Última fotografía validada en este repositorio:

| Dataset | Período | Filas | Bancos en el último mes |
|---|---:|---:|---:|
| Balance | ene. 2003-jul. 2026 | 8.183.806 | 23 |
| Pérdidas y ganancias | ene. 2003-jul. 2026 | 758.528 | 23 |
| CAMEL | ene. 2003-jul. 2026 | 230.999 | 23 |

La cifra vigente no se mantiene a mano en la interfaz: la portada lee `master_data/metadata.json`. Antes de publicar, el pipeline exige que los tres Parquet lleguen al mismo mes y que las 23 entidades estén presentes en ese corte.

## Qué permite analizar

La aplicación tiene cuatro módulos:

1. **Panorama:** activos, cartera, depósitos, patrimonio, participación y crecimiento anual.
2. **Balance General:** series históricas, jerarquía contable, participación, heatmaps y rankings.
3. **Pérdidas y Ganancias:** márgenes, resultados mensuales y acumulados móviles de 12 meses.
4. **CAMEL:** solvencia, calidad de activos, gestión, rentabilidad y liquidez.

Los rankings muestran todas las entidades disponibles. Los comparadores permiten seleccionar hasta 10 bancos simultáneamente para conservar legibilidad y rendimiento.

## Arquitectura resumida

```text
Superintendencia de Bancos
        │  23 ZIP por entidad
        ▼
descargar.py + fuente_bancos.py
        │  valida ZIP, XLSX, hojas BAL/PYG/CAMEL y fecha interna
        ▼
procesar_balance.py ─┐
procesar_pyg.py      ├─► master_data/*.parquet + metadata.json
procesar_camel.py   ─┘
        │
        ▼
validar_actualizacion.py
        │  fecha, esquema, 23 bancos, meses, claves e historia
        ▼
GitHub main ─► Streamlit Community Cloud
```

El flujo completo y sus decisiones están en [docs/ARQUITECTURA.md](docs/ARQUITECTURA.md).

## Inicio rápido

Requiere Python 3.11 recomendado.

```bash
git clone https://github.com/jp1309/bancos.git
cd bancos
python -m venv .venv
```

Activación del entorno:

```powershell
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
```

```bash
# Linux/macOS
source .venv/bin/activate
```

Instalación y ejecución:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m streamlit run Inicio.py
```

Abrir `http://localhost:8501`. La guía paso a paso está en [QUICKSTART.md](QUICKSTART.md).

## Actualización de datos

La vía recomendada es el workflow **Actualizar Datos Bancarios** en GitHub Actions. Se ejecuta diariamente del 6 al 20 de cada mes a las 13:00 UTC, equivalente a las 08:00 de Ecuador continental (UTC-5). Si el portal aún anuncia el corte anterior, termina sin descargar los 23 boletines; cuando el mes aparece, valida el contenido interno antes de publicar.

Ejecución manual local:

```bash
python -m pip install -r requirements-scraping.txt
python scripts/actualizar_datos.py
```

Códigos de salida del orquestador:

| Código | Significado | Acción |
|---:|---|---|
| `0` | Actualización completa o publicación ya vigente | No requiere corrección |
| `2` | La fuente oficial aún no avanzó | No-op; esperar el siguiente intento |
| Otro | Fallo real de descarga, ETL o validación | Revisar logs; no publicar |

No se debe forzar un commit cuando el proceso devuelve `2`. El detalle operativo está en [docs/AUTOMATIZACION.md](docs/AUTOMATIZACION.md).

## Validación

```bash
python -m unittest discover -s tests -v
python scripts/validar_actualizacion.py
```

La puerta de publicación comprueba:

- existencia y lectura de los tres Parquet;
- columnas obligatorias y claves sin duplicados;
- continuidad mensual global;
- fecha máxima igual al mes objetivo;
- exactamente 23 bancos únicos en cada dataset y 23 en el último mes;
- coherencia con `metadata.json`;
- conservación de meses y bancos ya publicados cuando existe un estado anterior.

## Estructura principal

```text
Inicio.py                       Portada multipágina
dashboard_metadata.py          Resumen dinámico de metadata
pages/                          Módulos Streamlit
utils/                          Carga, calidad y gráficos compartidos
config/indicator_mapping.py     Códigos, etiquetas y colores
scripts/                        Descarga, ETL, validación y orquestación
master_data/                    Parquet y metadata publicados
tests/                          Pruebas unitarias
docs/                           Documentación operativa y técnica
.github/workflows/              Automatización mensual
```

`app.py` está vacío y no es el punto de entrada. Streamlit debe ejecutar `Inicio.py`.

## Documentación

| Documento | Propósito |
|---|---|
| [Índice técnico](docs/README.md) | Mapa de documentos y fuentes de verdad |
| [Automatización](docs/AUTOMATIZACION.md) | GitHub Actions, calendario, exit codes y monitoreo |
| [Operación y recuperación](docs/OPERACION_Y_RECUPERACION.md) | Runbook, incidentes, rollback y recuperación |
| [Diccionario de datos](docs/DICCIONARIO_DATOS.md) | Esquemas, claves, unidades y semántica |
| [Arquitectura](docs/ARQUITECTURA.md) | Flujo fuente-ETL-Parquet-Streamlit |
| [Contribución](CONTRIBUTING.md) | Estándares, pruebas y checklist de cambios |

## Alcance y uso responsable

- Los valores monetarios provienen de la fuente en miles de USD y la interfaz los convierte a millones cuando corresponde.
- Los indicadores CAMEL se almacenan como proporciones y se muestran como porcentajes.
- PyG contiene valores acumulados oficiales, valores mensuales desacumulados y sumas móviles de 12 meses.
- El dashboard es una herramienta analítica; no sustituye estados financieros auditados ni pronunciamientos regulatorios.
- Los datos oficiales conservan sus términos y atribución de origen; la licencia MIT cubre el software del repositorio.

## Soporte

Para errores reproducibles, abrir un [issue](https://github.com/jp1309/bancos/issues) incluyendo módulo, fecha, banco, captura y pasos para reproducirlo. Para incidentes de actualización, adjuntar el enlace del run de GitHub Actions.
