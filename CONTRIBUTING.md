# Guía de Contribución

¡Gracias por tu interés en contribuir al proyecto Radar Bancario Ecuador! Este documento proporciona directrices para contribuir al proyecto.

## Cómo Contribuir

### Reportar Bugs

Si encuentras un bug, por favor abre un issue incluyendo:
- Descripción clara del problema
- Pasos para reproducirlo
- Comportamiento esperado vs. comportamiento actual
- Screenshots si es aplicable
- Información del entorno (versión de Python, Streamlit, sistema operativo)

### Sugerir Mejoras

Para sugerir mejoras o nuevas funcionalidades:
- Abre un issue describiendo la mejora propuesta
- Explica el caso de uso y el valor que agregaría
- Si es posible, proporciona ejemplos o mockups

### Pull Requests

1. **Fork el repositorio** y crea tu branch desde `main`
2. **Naming**: Usa nombres descriptivos para tus branches (ej: `feature/exportar-excel`, `fix/calculo-morosidad`)
3. **Código**:
   - Sigue las convenciones de estilo de Python (PEP 8)
   - Mantén la consistencia con el código existente
   - Comenta el código donde sea necesario
   - Actualiza la documentación si es relevante
4. **Testing**:
   - Prueba tus cambios localmente con `streamlit run Inicio.py`
   - Verifica que no rompas funcionalidades existentes
5. **Commits**:
   - Usa mensajes de commit descriptivos en español
   - Un commit por cambio lógico
6. **Pull Request**:
   - Describe claramente qué cambia y por qué
   - Referencia issues relacionados
   - Incluye screenshots si hay cambios visuales

## Estructura del Código

### Organización de Archivos

- `Inicio.py`: Página principal, solo configuración y presentación
- `pages/`: Módulos independientes de análisis
- `utils/`: Funciones compartidas (carga de datos, validación)
- `config/`: Configuraciones y mapeos estáticos

### Convenciones de Código

#### Nombres de Variables
```python
# Español para variables de negocio
banco = "Pichincha"
fecha_inicio = pd.Timestamp("2020-01-01")
total_activos = 1000000

# Inglés para variables técnicas está permitido
df = pd.DataFrame()
fig = go.Figure()
```

#### Funciones
```python
def cargar_datos_balance():
    """Carga y valida datos del balance general.

    Returns:
        tuple: (DataFrame con datos, dict con métricas de calidad)
    """
    pass
```

#### Componentes de Streamlit
```python
# Usar cache cuando sea apropiado
@st.cache_data
def calcular_indicadores(df: pd.DataFrame) -> pd.DataFrame:
    pass

# Nomenclatura clara para widgets
banco_seleccionado = st.selectbox(
    "Seleccione un banco",
    options=lista_bancos,
    key="selector_banco_panorama"  # Keys descriptivos
)
```

### Estilo Visual

#### Colores
Mantén consistencia con el tema azul:
```python
COLORES = {
    'principal': '#2c5282',
    'secundario': '#2b6cb0',
    'oscuro': '#1a365d',
    'texto_claro': '#718096',
    'texto': '#4a5568'
}
```

#### Layout
- Usa `st.columns()` para layouts responsivos
- Mantén márgenes consistentes
- Prioriza simplicidad sobre complejidad visual

## Áreas de Contribución Prioritarias

### Alta Prioridad
1. **Módulo de Calidad de Datos**: Dashboard de completitud y cobertura
2. **Tests Unitarios**: Para funciones de `utils/`
3. **Optimización de Performance**: Cache más granular, queries optimizadas
4. **Documentación**: Comentarios en código, docstrings

### Media Prioridad
1. **Módulo de Perfil Individual**: Análisis por banco
2. **Exportación**: Funcionalidad para exportar a Excel/PDF
3. **Comparador Avanzado**: Gráfico radar, correlaciones
4. **Responsividad**: Mejorar visualización en móviles

### Baja Prioridad
1. **Análisis Predictivo**: Forecasting de indicadores
2. **Alertas**: Sistema de notificaciones de eventos
3. **API REST**: Endpoints para integración

## Directrices de Datos

### Códigos Contables
- Usa siempre `config/indicator_mapping.py` para mapeos
- No busques por texto, usa códigos fijos
- Documenta nuevos códigos agregados

### Validación
- Filtra valores nulos antes de visualizar
- Valida jerarquías de cuentas
- Maneja casos edge (bancos sin datos, fechas faltantes)

### Performance
- Usa `@st.cache_data` para operaciones costosas
- Evita cargar datos completos si solo necesitas un subset
- Optimiza groupby y merge operations

## Código de Conducta

- Sé respetuoso y constructivo
- Acepta feedback con profesionalismo
- Prioriza la calidad sobre la cantidad
- Documenta decisiones técnicas importantes

## Preguntas

Si tienes preguntas sobre cómo contribuir, abre un issue con la etiqueta `question`.

---

¡Gracias por contribuir al Radar Bancario Ecuador! 🇪🇨
