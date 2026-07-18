# Inicio rápido

Esta guía cubre tres tareas: ejecutar el dashboard, validar los datos y lanzar una actualización mensual.

## 1. Preparar el entorno

Se recomienda Python 3.11, la misma versión usada en GitHub Actions.

```bash
git clone https://github.com/jp1309/bancos.git
cd bancos
python -m venv .venv
```

```powershell
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
```

```bash
# Linux/macOS
source .venv/bin/activate
```

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## 2. Ejecutar Streamlit

```bash
python -m streamlit run Inicio.py
```

Abrir `http://localhost:8501`.

Comprobación mínima:

- Inicio muestra el mismo mes que `master_data/metadata.json`.
- Panorama carga 23 bancos en el último corte.
- Balance, PyG y CAMEL abren sin excepción.

## 3. Ejecutar pruebas y puerta de datos

Para las pruebas completas también se necesitan las dependencias de procesamiento:

```bash
python -m pip install -r requirements-scraping.txt
python -m unittest discover -s tests -v
python scripts/validar_actualizacion.py
```

Una validación correcta termina con `VALIDACION MENSUAL OK` y resume filas, bancos y fecha máxima de los tres datasets.

## 4. Actualizar datos localmente

Requisitos adicionales:

- Google Chrome estable;
- conexión al portal de la Superintendencia;
- espacio temporal suficiente para ZIP, XLSX y respaldo de Parquet.

```bash
python scripts/actualizar_datos.py
```

Interpretación del resultado:

- `0`: actualización correcta o datos ya completos;
- `2`: la fuente todavía no publicó el mes objetivo; no es un error;
- otro código: fallo real; el orquestador restaura los datos maestros anteriores.

No ejecute los procesadores por separado salvo diagnóstico. El orquestador agrega respaldo, validación y rollback.

## 5. Ejecutar en GitHub

1. Abrir [GitHub Actions](https://github.com/jp1309/bancos/actions/workflows/actualizar-datos.yml).
2. Elegir **Run workflow**.
3. Confirmar la rama `main`.
4. Esperar el resultado del job `actualizar-datos`.

Desde GitHub CLI:

```bash
gh workflow run actualizar-datos.yml --repo jp1309/bancos --ref main
gh run list --repo jp1309/bancos --workflow actualizar-datos.yml --limit 3
```

## Problemas frecuentes

### La aplicación no inicia

```bash
python -m streamlit --version
python -m pip install -r requirements.txt
```

Confirme que está ejecutando `Inicio.py`, no `app.py`.

### Falta un Parquet

Debe existir:

```text
master_data/balance.parquet
master_data/pyg.parquet
master_data/camel.parquet
master_data/metadata.json
master_data/update_status.json
```

Restaure una versión conocida; no genere solo uno de los tres archivos para publicarlo aisladamente. Consulte [docs/OPERACION_Y_RECUPERACION.md](docs/OPERACION_Y_RECUPERACION.md).

### Streamlit muestra una versión anterior

1. Confirme que el commit está en `main`.
2. Confirme que Streamlit Cloud apunta a `jp1309/bancos`, `main`, `Inicio.py`.
3. Espere el redespliegue o use **Reboot app** en Streamlit Cloud.
4. Recargue la aplicación y compare el mes visible con `metadata.json`.

## Siguiente lectura

- [README principal](README.md)
- [Automatización mensual](docs/AUTOMATIZACION.md)
- [Diccionario de datos](docs/DICCIONARIO_DATOS.md)
- [Arquitectura](docs/ARQUITECTURA.md)
