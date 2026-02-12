# -*- coding: utf-8 -*-
"""
Procesa la hoja PYG (Pérdidas y Ganancias) de los archivos Excel.

Lógica especial:
- Los datos son acumulados mes a mes dentro de cada año
- Se desacumulan para obtener el valor de cada mes individual
- Se calcula suma móvil de 12 meses para comparabilidad

Estructura de la hoja PYG:
- Códigos de cuenta: columna A, desde fila 6
- Nombres de cuenta: columna B
- Datos: desde columna C
- Fechas: fila 5, desde columna C
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import sys
import warnings

warnings.filterwarnings('ignore')

# Agregar directorio de scripts al path para importar config
sys.path.insert(0, str(Path(__file__).parent))
import config

# Configuración
CARPETA_DATOS = Path(config.get_carpeta_salida()) / "archivos_excel"
CARPETA_SALIDA = Path("master_data")

# Códigos para cuentas resumen (filas con "--")
CODIGOS_RESUMEN = {
    'MARGEN NETO DE INTERESES': 'MNI',
    'MARGEN BRUTO FINANCIERO': 'MBF',
    'MARGEN NETO FINANCIERO': 'MNF',
    'MARGEN DE INTERMEDIACION': 'MDI',
    'MARGEN OPERACIONAL': 'MOP',
    'GANANCIA O PERDIDA ANTES DE IMPUESTOS': 'GAI',
    'GANANCIA O PERDIDA DEL EJERCICIO': 'GDE',
}


def limpiar_nombre_cuenta(nombre: str) -> str:
    """Limpia el nombre de la cuenta para usar como clave."""
    if pd.isna(nombre):
        return ''
    nombre = str(nombre).upper()
    nombre = nombre.replace('Á', 'A').replace('É', 'E').replace('Í', 'I')
    nombre = nombre.replace('Ó', 'O').replace('Ú', 'U').replace('Ñ', 'N')
    return nombre


def obtener_codigo_resumen(nombre: str) -> str:
    """Obtiene el código para una cuenta resumen."""
    nombre_limpio = limpiar_nombre_cuenta(nombre)
    for clave, codigo in CODIGOS_RESUMEN.items():
        if clave in nombre_limpio:
            return codigo
    return None


def procesar_archivo_pyg(ruta_excel: Path) -> pd.DataFrame:
    """Procesa la hoja PYG de un archivo Excel."""
    try:
        # Extraer nombre del banco de la ruta
        nombre_banco = ruta_excel.parent.name.split()[0]

        # Leer hoja PYG sin encabezado
        df_raw = pd.read_excel(ruta_excel, sheet_name='PYG', header=None)

        if df_raw.shape[0] < 10 or df_raw.shape[1] < 5:
            print(f"  [WARN] Archivo muy pequeño: {ruta_excel.name}")
            return pd.DataFrame()

        # Extraer fechas de la fila 5 (índice 4), desde columna C (índice 2)
        fechas_raw = df_raw.iloc[4, 2:].values
        fechas = []
        for f in fechas_raw:
            if pd.notna(f):
                if isinstance(f, datetime):
                    fechas.append(f)
                elif isinstance(f, str):
                    try:
                        fechas.append(pd.to_datetime(f))
                    except:
                        break
                else:
                    break
            else:
                break

        if len(fechas) == 0:
            print(f"  [WARN] Sin fechas válidas: {ruta_excel.name}")
            return pd.DataFrame()

        # Procesar filas de datos (desde fila 6, índice 5)
        registros = []

        for idx in range(5, min(140, len(df_raw))):
            codigo_raw = df_raw.iloc[idx, 0]
            nombre = df_raw.iloc[idx, 1]

            # Determinar código
            if pd.isna(codigo_raw):
                continue

            codigo_str = str(codigo_raw).strip()

            if codigo_str == '--':
                # Cuenta resumen
                codigo = obtener_codigo_resumen(nombre)
                if codigo is None:
                    continue
            elif codigo_str == 'nan':
                continue
            else:
                codigo = codigo_str

            # Limpiar nombre
            if pd.isna(nombre):
                continue
            nombre_limpio = str(nombre).strip()

            # Extraer valores
            valores = df_raw.iloc[idx, 2:2+len(fechas)].values

            for i, (fecha, valor) in enumerate(zip(fechas, valores)):
                if pd.notna(valor):
                    try:
                        valor_num = float(valor)
                        registros.append({
                            'banco': nombre_banco,
                            'fecha': pd.Timestamp(fecha),
                            'codigo': codigo,
                            'cuenta': nombre_limpio,
                            'valor_acumulado': valor_num
                        })
                    except (ValueError, TypeError):
                        pass

        if len(registros) == 0:
            return pd.DataFrame()

        df = pd.DataFrame(registros)
        return df

    except Exception as e:
        print(f"  [ERROR] {ruta_excel.name}: {e}")
        return pd.DataFrame()


def desacumular_valores(df: pd.DataFrame) -> pd.DataFrame:
    """
    Desacumula los valores para obtener el valor de cada mes individual.

    Lógica:
    - Enero: valor_mes = valor_acumulado (primer mes del año)
    - Feb-Dic: valor_mes = valor_acumulado - valor_acumulado_mes_anterior
    """
    if df.empty:
        return df

    df = df.sort_values(['banco', 'codigo', 'fecha']).copy()
    df['ano'] = df['fecha'].dt.year
    df['mes'] = df['fecha'].dt.month

    # Calcular valor del mes anterior (dentro del mismo banco, código y año)
    df['valor_anterior'] = df.groupby(['banco', 'codigo', 'ano'])['valor_acumulado'].shift(1)

    # Desacumular: para enero (mes=1) o si no hay anterior, usar valor acumulado directamente
    # Para otros meses, restar el valor anterior
    df['valor_mes'] = np.where(
        (df['mes'] == 1) | (df['valor_anterior'].isna()),
        df['valor_acumulado'],
        df['valor_acumulado'] - df['valor_anterior']
    )

    return df


def calcular_suma_movil_12m(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula la suma móvil de 12 meses para cada banco/código.
    Esto permite comparar cualquier mes con cualquier otro.
    """
    if df.empty:
        return df

    df = df.sort_values(['banco', 'codigo', 'fecha']).copy()

    # Calcular suma móvil de 12 meses
    df['valor_12m'] = df.groupby(['banco', 'codigo'])['valor_mes'].transform(
        lambda x: x.rolling(window=12, min_periods=12).sum()
    )

    return df


def main():
    print("=" * 60)
    print("PROCESAMIENTO DE HOJA PYG (PÉRDIDAS Y GANANCIAS)")
    print("=" * 60)

    # Crear carpeta de salida
    CARPETA_SALIDA.mkdir(exist_ok=True)

    # Buscar archivos Excel
    archivos = list(CARPETA_DATOS.glob("**/*.xlsx"))
    print(f"\nArchivos encontrados: {len(archivos)}")

    if len(archivos) == 0:
        print("[ERROR] No se encontraron archivos Excel")
        return

    # Procesar cada archivo
    dataframes = []

    for i, archivo in enumerate(archivos):
        print(f"\n[{i+1}/{len(archivos)}] {archivo.parent.name}")
        df = procesar_archivo_pyg(archivo)
        if not df.empty:
            dataframes.append(df)
            print(f"  -> {len(df):,} registros")

    if len(dataframes) == 0:
        print("\n[ERROR] No se procesaron datos")
        return

    # Combinar todos los DataFrames
    print("\n" + "-" * 40)
    print("Combinando datos...")
    df_combinado = pd.concat(dataframes, ignore_index=True)
    print(f"Total registros acumulados: {len(df_combinado):,}")

    # Desacumular valores
    print("\nDesacumulando valores mensuales...")
    df_desacumulado = desacumular_valores(df_combinado)
    print(f"Registros después de desacumular: {len(df_desacumulado):,}")

    # Calcular suma móvil de 12 meses
    print("\nCalculando suma móvil de 12 meses...")
    df_final = calcular_suma_movil_12m(df_desacumulado)

    # Seleccionar columnas finales
    columnas_finales = ['banco', 'fecha', 'codigo', 'cuenta',
                        'valor_acumulado', 'valor_mes', 'valor_12m']
    df_final = df_final[columnas_finales]

    # Estadísticas
    print("\n" + "=" * 40)
    print("RESUMEN")
    print("=" * 40)
    print(f"Bancos: {df_final['banco'].nunique()}")
    print(f"Fechas: {df_final['fecha'].nunique()}")
    print(f"Cuentas únicas: {df_final['codigo'].nunique()}")
    print(f"Registros totales: {len(df_final):,}")

    # Fechas disponibles
    print(f"\nRango de fechas: {df_final['fecha'].min()} a {df_final['fecha'].max()}")

    # Verificar suma móvil
    registros_con_12m = df_final['valor_12m'].notna().sum()
    print(f"Registros con valor_12m: {registros_con_12m:,} ({registros_con_12m/len(df_final)*100:.1f}%)")

    # Guardar
    ruta_salida = CARPETA_SALIDA / "pyg.parquet"
    df_final.to_parquet(ruta_salida, index=False)
    print(f"\n[OK] Guardado: {ruta_salida}")
    print(f"    Tamaño: {ruta_salida.stat().st_size / 1024 / 1024:.1f} MB")

    # Mostrar muestra de cuentas principales
    print("\n" + "-" * 40)
    print("Cuentas principales procesadas:")
    cuentas_principales = df_final[
        (df_final['codigo'].str.len() <= 3) |
        (df_final['codigo'].isin(['MNI', 'MBF', 'MNF', 'MDI', 'MOP', 'GAI', 'GDE']))
    ]['codigo'].unique()
    for c in sorted(cuentas_principales):
        nombre = df_final[df_final['codigo'] == c]['cuenta'].iloc[0]
        print(f"  {c}: {nombre}")


if __name__ == "__main__":
    main()
