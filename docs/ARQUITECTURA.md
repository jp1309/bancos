# Arquitectura del Radar Bancario

## Vista general

```text
┌──────────────────────────────────────────────────────────────┐
│ Superintendencia de Bancos: Boletines de Series por Entidad │
└───────────────────────────┬──────────────────────────────────┘
                            │ Selenium + descargas HTTP
                            ▼
┌──────────────────────────────────────────────────────────────┐
│ Staging: 23 ZIP → 23 XLSX → BAL / PYG / CAMEL              │
│ fuente_bancos.py valida estructura y fecha interna           │
└───────────────────────────┬──────────────────────────────────┘
                            │
             ┌──────────────┼──────────────┐
             ▼              ▼              ▼
       Balance ETL       PyG ETL        CAMEL ETL
             │              │              │
             └──────────────┼──────────────┘
                            ▼
┌──────────────────────────────────────────────────────────────┐
│ master_data: tres Parquet + metadata + estado               │
└───────────────────────────┬──────────────────────────────────┘
                            │ puerta de calidad
                            ▼
                   GitHub main / versionado
                            │
                            ▼
                Streamlit Community Cloud
```

## Capas

### 1. Fuente

`scripts/config.py` calcula el mes anterior y define el portal `bancos-2/`, el número esperado de entidades y los tiempos de Selenium.

`scripts/descargar.py` navega el portal, obtiene los ZIP y promueve el staging solo después de validarlo. `scripts/fuente_bancos.py` inspecciona ZIP/XLSX y fecha interna.

Decisión clave: una URL estable o un HTTP 200 no demuestra avance; el contenido puede seguir en el mes anterior.

### 2. Transformación

- `procesar_balance.py`: normaliza la hoja BAL, calcula jerarquía y consolida historia.
- `procesar_pyg.py`: conserva acumulados, desacumula meses y calcula rolling de 12 meses.
- `procesar_camel.py`: extrae 39 indicadores y los categoriza.

Cada procesador falla si encuentra entidades ausentes, vacías o no procesables y escribe el Parquet mediante temporal y reemplazo.

### 3. Publicación de datos

`master_data/` es la interfaz estable entre ETL y frontend. Los cinco artefactos versionados forman una unidad lógica.

`validar_actualizacion.py` actúa como publication gate y usa PyArrow para inspección de esquema y lecturas acotadas de claves.

### 4. Aplicación

`Inicio.py` es el entrypoint multipágina. `dashboard_metadata.py` deriva los KPIs de portada desde `metadata.json`.

Páginas:

- `1_Panorama.py`
- `2_Balance_General.py`
- `3_Pérdidas_y_Ganancias.py`
- `4_CAMEL.py`

`utils/data_loader.py` centraliza lectura, tipado, filtrado y caché. Las columnas textuales repetitivas se mantienen categóricas para controlar memoria. Los `groupby` categóricos usan `observed=True` para evitar expansiones cartesianas.

`utils/charts.py` contiene componentes Plotly reutilizables y `config/indicator_mapping.py` gobierna códigos, etiquetas y colores.

### 5. Despliegue

GitHub Actions publica datos en `main`. Streamlit Community Cloud observa esa rama y ejecuta `Inicio.py`. La aplicación no consulta el portal oficial en tiempo real: consume los Parquet versionados.

## Transacción mensual

La frontera transaccional abarca:

1. staging de fuente;
2. respaldo de artefactos publicados;
3. tres procesadores;
4. validación conjunta;
5. commit de la unidad de publicación.

Un fallo antes del commit no debe modificar la publicación remota. Un fallo de ETL local restaura el respaldo temporal.

## Rendimiento

- Parquet columnar reduce I/O y almacenamiento.
- Categorías/dictionary encoding reducen memoria de strings repetidos.
- `@st.cache_data` evita recargar datos en cada interacción.
- Las funciones leen columnas acotadas cuando solo necesitan fechas o claves.
- Los selectores limitan comparaciones simultáneas, pero rankings y cobertura incluyen todas las entidades.

## Seguridad e integridad

- No hay credenciales de la fuente; los boletines son públicos.
- GitHub Actions usa `GITHUB_TOKEN` con `contents: write` limitado al workflow.
- La extracción rechaza rutas ZIP inseguras.
- El pipeline no ejecuta macros de los XLSX.
- Los datos se publican solo después de una puerta determinística.

## Decisiones y tradeoffs

### Parquet dentro de Git

Ventajas: despliegue sencillo, reproducibilidad por commit y rollback directo. Costos: repositorio más pesado y commits de datos binarios. Los tamaños actuales permanecen bajo el límite duro de GitHub, aunque deben vigilarse.

### Reescritura de Balance

Balance consolida una historia extensa y puede ser la etapa más costosa. La escritura atómica y las columnas categóricas priorizan seguridad sobre una actualización mínima de bytes.

### Número fijo de bancos

La expectativa de 23 funciona como alarma contra fuentes parciales. El costo es que un cambio institucional legítimo exige intervención humana y actualización coordinada de configuración, pruebas y documentación.

## Extender el sistema

Para agregar un dataset:

1. definir fuente y clave estable;
2. crear procesador con salida atómica;
3. agregar esquema y clave a `DATASETS` del validador;
4. incluirlo en respaldo, rollback y commit de Actions;
5. documentarlo en el diccionario;
6. añadir pruebas de cobertura, fecha, duplicados e historia;
7. integrar el loader y la página Streamlit.

No conecte una página directamente a archivos temporales o descargas crudas.
