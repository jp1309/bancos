# Estructura de los Archivos Excel de Bancos

## Información General

Cada archivo Excel descargado de la Superintendencia de Bancos contiene datos históricos mensuales de un banco desde 2003 hasta el mes más reciente disponible.

**Archivo analizado**: Banco Guayaquil - Diciembre 2025

---

## Hojas del Archivo (14 hojas en total)

### 1. **BAL** - Balance General (Situación Nominal)
- **Descripción**: Comparativo histórico del Balance General del banco
- **Contenido**: Estados de situación financiera con todas las cuentas contables
- **Estructura**:
  - Columna A: CÓDIGO (código contable)
  - Columna B: CUENTA (nombre de la cuenta)
  - Columnas C en adelante: Fechas mensuales desde 2003-01-31 hasta diciembre 2025
- **Datos**: Valores en miles de dólares
- **Filas**: ~1,395 cuentas contables
- **Columnas**: ~281 (2 de metadata + ~279 meses de datos)

**Ejemplo de cuentas**:
- 1. ACTIVO
- 11. FONDOS DISPONIBLES
- 12. OPERACIONES INTERBANCARIAS
- 13. INVERSIONES
- 14. CARTERA DE CRÉDITOS
- etc.

---

### 2. **PYG** - Estado de Resultados (Pérdidas y Ganancias)
- **Descripción**: Comparativo histórico del Estado de Resultados
- **Contenido**: Ingresos, gastos, y resultados del ejercicio
- **Estructura**: Idéntica a BAL
  - Columna A: CÓDIGO
  - Columna B: CUENTA
  - Columnas C+: Datos mensuales desde 2003
- **Datos**: Valores en miles de dólares
- **Filas**: ~1,000+ cuentas de resultados

**Ejemplo de cuentas**:
- 51. INGRESOS FINANCIEROS
- 52. GASTOS FINANCIEROS
- 53. MARGEN FINANCIERO BRUTO
- 54. GASTOS DE OPERACIÓN
- 56. OTROS INGRESOS Y GASTOS
- 36. RESULTADO DEL EJERCICIO

---

### 3. **GRUPOS CTAS** - Principales Grupos de Cuentas de Balance
- **Descripción**: Resumen agrupado del Balance General
- **Contenido**: Principales categorías del balance (sin detalle granular)
- **Estructura**: Similar a BAL pero con menos filas
  - Grupos principales: ACTIVO, PASIVO, PATRIMONIO
  - Subcategorías principales solamente
- **Datos**: Valores en miles de dólares

---

### 4. **BAL %** - Balance General en Porcentajes
- **Descripción**: Mismo contenido que BAL pero expresado en porcentajes
- **Contenido**: Composición porcentual de cada cuenta respecto al total de activos
- **Estructura**: Idéntica a BAL
- **Datos**: Valores porcentuales (%)
- **Utilidad**: Análisis de estructura financiera y evolución de composición

---

### 5. **PYG %** - Estado de Resultados en Porcentajes
- **Descripción**: Mismo contenido que PYG pero expresado en porcentajes
- **Contenido**: Análisis vertical del estado de resultados
- **Estructura**: Idéntica a PYG
- **Datos**: Valores porcentuales (%)
- **Utilidad**: Análisis de márgenes y estructura de costos

---

### 6. **INDIC CARTERA** - Indicadores de Cartera de Créditos
- **Descripción**: Indicadores específicos de la calidad de cartera
- **Contenido**:
  - Morosidad por tipo de cartera
  - Cobertura de provisiones
  - Cartera improductiva / cartera bruta
  - Cartera vencida
- **Estructura**:
  - Fila 1-3: Encabezados
  - Columna A: Indicador
  - Columnas B+: Series mensuales
- **Datos**: Porcentajes y ratios

---

### 7. **MET** - Metodología de Cálculo
- **Descripción**: Definiciones y fórmulas de todos los indicadores
- **Contenido**:
  - Nombre del indicador
  - Fórmula de cálculo
  - Componentes de la fórmula
  - Referencias a códigos contables
- **Estructura**: Documentación de metodología
- **Utilidad**: Entender cómo se calculan los indicadores financieros

---

### 8. **GRAF CARTERA** - Gráficos de Cartera
- **Descripción**: Datos preparados para gráficos de cartera
- **Contenido**: Series de tiempo de principales indicadores de cartera
- **Estructura**: Tablas optimizadas para visualización
- **Datos**: Valores y porcentajes formateados

---

### 9. **INDICAD** - Indicadores Financieros
- **Descripción**: Todos los indicadores financieros del banco
- **Contenido**:
  - **Indicadores de Liquidez**: Fondos disponibles / depósitos
  - **Indicadores de Solvencia**: Patrimonio / activos
  - **Indicadores de Rentabilidad**: ROA, ROE
  - **Indicadores de Eficiencia**: Gastos operacionales / activos
  - **Indicadores de Calidad de Activos**: Morosidad, provisiones
  - **Indicadores CAMEL**: Capital, Assets, Management, Earnings, Liquidity
- **Estructura**:
  - Columna A: Nombre del indicador
  - Columnas B+: Valores mensuales
- **Datos**: Porcentajes, ratios, índices
- **Filas**: ~100-150 indicadores

**Ejemplos de indicadores**:
- Suficiencia Patrimonial
- Morosidad de Cartera Total
- ROA (Return on Assets)
- ROE (Return on Equity)
- Intermediación Financiera
- Margen de Intermediación

---

### 10. **GRAF INDIC** - Gráficos de Indicadores
- **Descripción**: Datos preparados para gráficos de indicadores
- **Contenido**: Series de tiempo de indicadores principales
- **Estructura**: Tablas optimizadas para visualización
- **Datos**: Valores formateados para gráficos

---

### 11. **CAMEL** - Sistema de Calificación CAMEL
- **Descripción**: Indicadores del sistema de evaluación CAMEL
- **Contenido**: 5 componentes del sistema CAMEL
  - **C**apital Adequacy (Suficiencia de Capital)
  - **A**sset Quality (Calidad de Activos)
  - **M**anagement (Gestión)
  - **E**arnings (Rentabilidad)
  - **L**iquidity (Liquidez)
- **Estructura**: Indicadores agrupados por categoría CAMEL
- **Datos**: Ratios e índices específicos de supervisión bancaria
- **Utilidad**: Evaluación de salud financiera según estándares internacionales

---

### 12. **ESTRUC CART** - Estructura de Cartera
- **Descripción**: Composición detallada de la cartera de créditos
- **Contenido**:
  - Cartera por tipo: Comercial, Consumo, Vivienda, Microcrédito
  - Cartera por calificación de riesgo: A, B, C, D, E
  - Cartera vigente vs vencida
  - Cartera reestructurada
  - Cartera refinanciada
- **Estructura**:
  - Desagregación por categorías
  - Series temporales mensuales
- **Datos**: Valores en miles de dólares y porcentajes

---

### 13. **FUENTES USOS** - Fuentes y Usos de Fondos
- **Descripción**: Análisis de origen y aplicación de fondos
- **Contenido**:
  - **Fuentes**: De dónde obtiene recursos el banco
    - Depósitos a la vista
    - Depósitos a plazo
    - Obligaciones financieras
    - Patrimonio
  - **Usos**: En qué se utilizan esos recursos
    - Cartera de créditos
    - Inversiones
    - Fondos disponibles
- **Estructura**: Tabla de fuentes y usos por periodo
- **Datos**: Valores en miles de dólares
- **Utilidad**: Análisis de gestión de fondos y transformación de plazos

---

### 14. **REFINA REES** - Refinanciamiento y Reestructuración
- **Descripción**: Detalle de cartera refinanciada y reestructurada
- **Contenido**:
  - Operaciones de crédito refinanciadas
  - Operaciones de crédito reestructuradas
  - Evolución temporal de estas operaciones
  - Indicadores de calidad de cartera refinanciada/reestructurada
- **Estructura**: Series temporales por tipo de operación
- **Datos**: Valores en miles de dólares
- **Utilidad**: Seguimiento de créditos problemáticos y medidas correctivas

---

## Características Comunes de Todas las Hojas

### Formato Temporal
- **Inicio**: Enero 2003 (2003-01-31)
- **Fin**: Diciembre 2025 (2025-12-31) - o el mes más reciente disponible
- **Frecuencia**: Mensual (último día de cada mes)
- **Total periodos**: ~279 meses (23 años aproximadamente)

### Estructura de Encabezados
```
Fila 1: Título de la hoja (ej: "COMPARATIVO DE SITUACIÓN NOMINAL")
Fila 2: Nombre del banco (ej: "BP GUAYAQUIL")
Fila 3: Unidad de medida (ej: "(En miles de dólares)")
Fila 4: Vacía
Fila 5: Encabezados de columnas (CÓDIGO, CUENTA, 2003-01-31, 2003-02-28, ...)
Fila 6+: Datos
```

### Valores Numéricos
- **Moneda**: USD (Dólares estadounidenses)
- **Escala**: Miles de dólares (ej: 1,234 = $1,234,000)
- **Formato**: Números con separadores de miles
- **Valores especiales**:
  - `NaN` o vacío = No aplica o dato no disponible
  - `0` = Valor cero
  - Negativos posibles en cuentas de resultados

---

## Uso Recomendado de Cada Hoja

| Hoja | Uso Principal |
|------|---------------|
| **BAL** | Análisis de activos, pasivos y patrimonio en valores absolutos |
| **PYG** | Análisis de ingresos, gastos y utilidad neta |
| **GRUPOS CTAS** | Vista resumida del balance para análisis rápido |
| **BAL %** | Análisis de composición y estructura del balance |
| **PYG %** | Análisis de márgenes y estructura de costos |
| **INDIC CARTERA** | Evaluación de calidad de cartera de créditos |
| **MET** | Consulta de definiciones y fórmulas |
| **GRAF CARTERA** | Datos listos para visualizaciones de cartera |
| **INDICAD** | Análisis integral de indicadores financieros |
| **GRAF INDIC** | Datos listos para visualizaciones de indicadores |
| **CAMEL** | Evaluación supervisora según estándares internacionales |
| **ESTRUC CART** | Análisis detallado de composición de cartera |
| **FUENTES USOS** | Análisis de gestión de liquidez y transformación de plazos |
| **REFINA REES** | Seguimiento de cartera problemática |

---

## Notas Importantes

1. **Consistencia entre bancos**: Todos los 24 bancos tienen la misma estructura de hojas y formato de datos.

2. **Actualización mensual**: Los archivos se actualizan mensualmente con nuevas columnas que representan el nuevo mes.

3. **Códigos contables**: Los códigos en columna A siguen el catálogo único de cuentas de la Superintendencia de Bancos del Ecuador.

4. **Datos históricos completos**: Permiten análisis de tendencias de largo plazo (23 años).

5. **Calidad de datos**: Datos oficiales auditados y reportados por cada banco a la Superintendencia.

---

## Ejemplo de Análisis Posibles

- **Evolución de morosidad** desde 2003 hasta 2025
- **Comparación entre bancos** de indicadores de solvencia
- **Análisis de crisis** (ej: impacto de COVID-19 en 2020)
- **Crecimiento de activos** por banco
- **Rentabilidad histórica** (ROA, ROE)
- **Estructura de fondeo** (depósitos vs deuda)
- **Transformación de plazos** (fuentes de corto plazo → usos de largo plazo)
- **Calidad de activos** (morosidad, provisiones, cartera improductiva)

---

**Fecha de análisis**: 2026-01-23
**Archivo base**: Banco Guayaquil - Diciembre 2025
