# Guía Rápida - Radar Bancario Ecuador

Esta guía te ayudará a poner en marcha el dashboard en pocos minutos.

## Requisitos Previos

- Python 3.8 o superior instalado
- Conexión a internet (para instalar dependencias)

## Instalación Rápida

### 1. Clonar el repositorio

```bash
git clone https://github.com/[tu-usuario]/bancos.git
cd bancos
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

O manualmente:

```bash
pip install streamlit pandas plotly pyarrow numpy
```

### 3. Ejecutar el dashboard

```bash
streamlit run Inicio.py
```

El dashboard se abrirá automáticamente en tu navegador en `http://localhost:8501`

Si deseas usar un puerto específico:

```bash
streamlit run Inicio.py --server.port 8502
```

## Estructura de Datos

El proyecto incluye datos precargados en formato Parquet en la carpeta `master_data/`:

- `balance.parquet` - Balance General (18 MB)
- `pyg.parquet` - Pérdidas y Ganancias (9.5 MB)
- `camel.parquet` - Indicadores CAMEL (1.6 MB)

**Período**: 2003-2025 (276 meses)
**Bancos**: 23 instituciones activas

## Navegación del Dashboard

El dashboard tiene 5 páginas principales:

### 🏠 Inicio
Página de bienvenida con descripción de todos los módulos.

### 📊 1. Panorama del Sistema
Vista consolidada del sistema bancario:
- KPIs principales (activos, cartera, depósitos, ROA, liquidez)
- Mapa de mercado (treemaps interactivos)
- Rankings por activos y pasivos
- Crecimiento año contra año

**Uso**: Selecciona un mes en el sidebar para ver el estado del sistema en ese período.

### 📈 2. Balance General
Análisis temporal de la estructura patrimonial:
- **Evolución Comparativa**: Gráficos de líneas para comparar bancos
- **Heatmap YoY**: Matriz de variación anual
- **Ranking**: Comparación para un mes específico

**Uso**:
1. Selecciona el nivel de cuenta jerárquico (1→2→4→6 dígitos)
2. Elige los bancos a comparar (máximo 10)
3. Ajusta el rango de fechas
4. Cambia entre modos: Absoluto, Indexado o Participación

### 💰 3. Pérdidas y Ganancias
Análisis de resultados y rentabilidad:
- Evolución de indicadores PyG (MNI, MBF, MNF, MDI, MOP, GAI, GDE)
- Rankings de rentabilidad

**Uso**:
1. Selecciona el indicador de resultados
2. Elige los bancos a comparar
3. Define el período de análisis

### 📉 4. Indicadores CAMEL
Evaluación bancaria multidimensional:
- **C**: Capital (Solvencia)
- **A**: Assets (Morosidad, Cobertura)
- **M**: Management (Eficiencia)
- **E**: Earnings (ROE, ROA)
- **L**: Liquidity (Fondos disponibles)

**Uso**:
1. Selecciona una dimensión CAMEL
2. Elige el indicador específico
3. Explora en 3 modos:
   - Análisis por Indicador (ranking actual)
   - Evolución Temporal (tendencias)
   - Heatmap Mensual (patrones temporales)

## Casos de Uso Comunes

### Ver el tamaño del sistema bancario actual

1. Ve a **Panorama del Sistema**
2. Selecciona el último mes disponible
3. Observa los KPIs en la parte superior

### Comparar el crecimiento de dos bancos

1. Ve a **Balance General → Evolución Comparativa**
2. Selecciona "1 - ACTIVO" (primer nivel)
3. Elige los 2 bancos en el selector
4. Cambia a modo "Indexado" para comparar crecimiento relativo
5. Ajusta el rango de fechas según necesites

### Analizar la morosidad de un banco en el tiempo

1. Ve a **Indicadores CAMEL**
2. Selecciona dimensión **A - Calidad de Activos**
3. Elige "Morosidad de la Cartera Total"
4. Ve a la pestaña **Evolución Temporal**
5. Selecciona el banco de interés
6. Define el período (por defecto desde Enero 2015)

### Ver qué banco es más rentable

1. Ve a **Pérdidas y Ganancias → Ranking de Bancos**
2. Selecciona "GDE - Ganancia del Ejercicio"
3. Elige el mes más reciente
4. Observa el gráfico de barras ordenado

### Comparar la participación de mercado

1. Ve a **Balance General → Evolución Comparativa**
2. Selecciona "1 - ACTIVO"
3. Elige todos los bancos grandes
4. Cambia a modo **Participación**
5. Observa cómo cambia la participación en el tiempo

## Consejos de Uso

### Rendimiento
- El primer carga de cada módulo puede tomar unos segundos (datos se cachean)
- Usa filtros para reducir el volumen de datos visualizados
- Cierra pestañas del navegador que no estés usando

### Visualizaciones
- **Hover**: Pasa el mouse sobre los gráficos para ver valores exactos
- **Zoom**: Click y arrastra en gráficos Plotly para hacer zoom
- **Reset**: Doble click para resetear zoom
- **Descargar**: Usa el ícono de cámara en gráficos para guardar imágenes

### Filtros
- Los filtros jerárquicos se actualizan automáticamente según disponibilidad
- Si no ves opciones en un nivel, significa que no hay subcuentas
- Los rangos de fechas están limitados a datos disponibles (2003-2025)

### Interpretación de Datos
- **Valores absolutos**: En millones de USD (M = millones)
- **Modo indexado**: Base 100 en el primer período seleccionado
- **Participación**: Porcentaje sobre total del sistema
- **YoY**: Variación año contra año (mismo mes del año anterior)
- **12M**: Valores acumulados últimos 12 meses

## Solución de Problemas

### El dashboard no inicia
```bash
# Verifica que Streamlit esté instalado
streamlit --version

# Reinstala si es necesario
pip install --upgrade streamlit
```

### Errores de datos faltantes
```bash
# Verifica que existan los archivos Parquet
ls master_data/*.parquet

# Deberías ver:
# balance.parquet
# pyg.parquet
# camel.parquet
```

### Gráficos no se muestran
- Verifica que Plotly esté instalado: `pip install plotly`
- Prueba otro navegador (Chrome o Firefox recomendados)
- Limpia cache: En el menú del dashboard → Settings → Clear cache

### El dashboard es lento
- Reduce el número de bancos seleccionados
- Acorta el rango de fechas
- Reinicia el servidor Streamlit

## Próximos Pasos

Una vez familiarizado con el dashboard:

1. Explora la documentación completa en [README.md](README.md)
2. Revisa la guía de contribución en [CONTRIBUTING.md](CONTRIBUTING.md)
3. Consulta el mapeo de códigos en `config/indicator_mapping.py`
4. Experimenta con diferentes combinaciones de filtros

## Soporte

Si encuentras problemas o tienes preguntas:
- Revisa la [documentación completa](README.md)
- Abre un issue en GitHub
- Consulta el código fuente (está documentado)

---

**Desarrollado por**: Juan Pablo Erráez T.

¡Disfruta explorando los datos bancarios de Ecuador! 🇪🇨
