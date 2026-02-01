# Visualización de Crecimiento Anual por Banco

## Descripción

Gráficos de barras horizontales que muestran el crecimiento anual de cada banco en dos métricas clave:
- **Cartera de Créditos**
- **Depósitos del Público**

## Características

### Cálculo
- Compara el mes seleccionado con el mismo mes del año anterior (12 meses atrás)
- Fórmula: `((Valor Actual - Valor Anterior) / Valor Anterior) * 100`

### Visualización
- **Orientación**: Barras horizontales
- **Ordenamiento**: De mayor a menor crecimiento (ascendente en Y)
- **Colores**: Escala RdYlGn (Rojo-Amarillo-Verde)
  - Rojo: Crecimiento negativo
  - Amarillo: Crecimiento bajo
  - Verde: Crecimiento alto
- **Rango de colores**: -10% (rojo) a 30% (verde)
- **Etiquetas**: Porcentaje mostrado al lado de cada barra
- **Línea de referencia**: Línea vertical punteada en 0%

### Altura Dinámica
- Altura mínima: 400px
- Altura calculada: `max(400, num_bancos * 20px)`
- Se ajusta automáticamente según la cantidad de bancos

## Ubicación

**Módulo**: `pages/1_Panorama.py`

**Sección**: "Crecimiento Anual por Banco"

## Código Relevante

### Estructura de Datos
```python
# Obtener fecha actual y año anterior
df_fecha_actual = df_balance[
    (df_balance['fecha'] == fecha_seleccionada) &
    (df_balance['codigo'] == codigo_cuenta)
][['banco', 'valor']].copy()

df_fecha_anterior = df_balance[
    (df_balance['fecha'] == fecha_anterior) &
    (df_balance['codigo'] == codigo_cuenta)
][['banco', 'valor']].copy()

# Merge y cálculo
df_crec = df_fecha_actual.merge(
    df_fecha_anterior,
    on='banco',
    suffixes=('_actual', '_anterior')
)

df_crec['crecimiento'] = (
    (df_crec['valor_actual'] - df_crec['valor_anterior']) /
    df_crec['valor_anterior'] * 100
)

# Ordenar de mayor a menor
df_crec = df_crec.sort_values('crecimiento', ascending=True)
```

### Gráfico con Plotly
```python
fig = go.Figure(go.Bar(
    x=df_crec['crecimiento'],
    y=df_crec['banco'],
    orientation='h',
    marker=dict(
        color=df_crec['crecimiento'],
        colorscale='RdYlGn',
        cmin=-10,
        cmax=30,
    ),
    text=df_crec['crecimiento'].apply(lambda x: f"{x:.1f}%"),
    textposition='outside'
))

fig.update_layout(
    title="Crecimiento Anual (%)",
    height=max(400, len(df_crec) * 20),
    xaxis_title="Crecimiento (%)",
    yaxis_title="",
    showlegend=False,
    margin=dict(l=10, r=10, t=40, b=10)
)

# Línea de referencia en 0
fig.add_vline(x=0, line_dash="dash", line_color="gray", line_width=1)
```

## Interpretación

### Colores
- **Verde oscuro**: Crecimiento superior al 30%
- **Verde claro**: Crecimiento entre 15-30%
- **Amarillo**: Crecimiento entre 0-15%
- **Naranja**: Crecimiento negativo entre -10% y 0%
- **Rojo**: Decrecimiento superior al -10%

### Posición
- **Arriba**: Bancos con mayor crecimiento
- **Abajo**: Bancos con menor crecimiento o decrecimiento

## Casos Especiales

### Sin Datos del Año Anterior
Si no existe información de 12 meses atrás:
```python
if fecha_anterior:
    # Generar gráfico
else:
    st.info("No hay datos del año anterior para comparar.")
```

### Bancos Nuevos
Los bancos que no existían hace 12 meses no aparecerán en el gráfico (se filtran automáticamente en el merge).

## Ventajas de esta Visualización

1. **Comparación Directa**: Fácil identificar ganadores y perdedores
2. **Tendencias Claras**: Los colores refuerzan el mensaje
3. **Compacta**: Muestra todos los bancos en un solo gráfico
4. **Contexto Temporal**: Se adapta al mes seleccionado
5. **Referencia Visual**: La línea en 0% marca claramente crecimiento/decrecimiento

## Mejoras Futuras Sugeridas

- [ ] Agregar tooltip con valores absolutos (millones USD)
- [ ] Opción para cambiar período de comparación (6 meses, 24 meses)
- [ ] Filtro para mostrar solo top N bancos
- [ ] Exportar datos a Excel
- [ ] Agregar promedio del sistema como línea de referencia

## Versión

- **Fecha de Implementación**: 25 de enero de 2026
- **Versión**: 1.0
- **Autor**: Dashboard Radar Bancario Ecuador

---

## Ejemplo Visual

```
Crecimiento Anual (%)
Cartera de Créditos

Banco A    ████████████████████████ 24.5%
Banco B    █████████████████ 18.2%
Banco C    ████████████ 12.8%
Banco D    ████████ 8.1%
...
Banco Z    ██ 2.3%
Banco Y    | -3.5% ██
           0
```

El banco con mayor crecimiento aparece arriba, y los de menor crecimiento (o decrecimiento) abajo.
