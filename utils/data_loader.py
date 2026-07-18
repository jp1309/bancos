# -*- coding: utf-8 -*-
"""
Carga centralizada de datos con validacion y limpieza.
"""

import pandas as pd
import streamlit as st
from pathlib import Path
from typing import Tuple, Dict, Any
import json

# Ruta base de datos
MASTER_DATA_DIR = Path(__file__).parent.parent / "master_data"


def _categorizar_columnas(df: pd.DataFrame, columnas: list[str]) -> pd.DataFrame:
    """Reduce memoria de columnas textuales repetitivas sin copiar todo el DataFrame."""
    for columna in columnas:
        if columna in df.columns and not isinstance(df[columna].dtype, pd.CategoricalDtype):
            df[columna] = df[columna].astype('category')
    return df


def _mascara_texto_valido(serie: pd.Series) -> pd.Series:
    """Filtra texto vacio de forma eficiente incluso si la serie es categorica."""
    if isinstance(serie.dtype, pd.CategoricalDtype):
        categorias_invalidas = [
            valor for valor in serie.cat.categories
            if not str(valor).strip()
        ]
        return serie.notna() & ~serie.isin(categorias_invalidas)
    return serie.notna() & serie.str.strip().ne('')


@st.cache_data(ttl=3600)
def cargar_balance() -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Carga balance.parquet con limpieza y metricas de calidad.

    Returns:
        Tuple[DataFrame, Dict]: DataFrame limpio y metricas de calidad
    """
    filepath = MASTER_DATA_DIR / "balance.parquet"

    if not filepath.exists():
        raise FileNotFoundError(f"No se encontro {filepath}")

    df = pd.read_parquet(filepath)
    registros_originales = len(df)
    df = _categorizar_columnas(df, ['banco', 'codigo', 'cuenta'])

    # 1. Filtrar cuentas vacias
    mask_cuenta_valida = _mascara_texto_valido(df['cuenta'])
    if not mask_cuenta_valida.all():
        df = df.loc[mask_cuenta_valida]

    # 2. Filtrar valores nulos en columnas clave
    df = df.dropna(subset=['banco', 'fecha'])

    # 3. Convertir fecha a datetime si no lo es
    if not pd.api.types.is_datetime64_any_dtype(df['fecha']):
        df['fecha'] = pd.to_datetime(df['fecha'])

    # Metricas de calidad
    calidad = {
        'registros_originales': registros_originales,
        'registros_limpios': len(df),
        'registros_eliminados': registros_originales - len(df),
        'pct_eliminados': round((registros_originales - len(df)) / registros_originales * 100, 2),
        'bancos': df['banco'].nunique(),
        'fechas': df['fecha'].nunique(),
        'fecha_min': df['fecha'].min(),
        'fecha_max': df['fecha'].max(),
        'nulos_valor': df['valor'].isna().sum(),
        'nulos_codigo': df['codigo'].isna().sum(),
    }

    return df, calidad


# =============================================================================
# FUNCIONES ELIMINADAS (ya no se usan en el dashboard):
# - cargar_indicadores() -> indicadores.parquet (eliminado)
# - cargar_cartera() -> cartera.parquet (eliminado)
# - cargar_fuentes_usos() -> fuentes_usos.parquet (eliminado)
#
# Solo se mantienen las 3 funciones esenciales:
# - cargar_balance() -> Hojas BAL (18 MB)
# - cargar_pyg() -> Hoja PYG (9.5 MB)
# - cargar_camel() -> Hoja CAMEL (1.6 MB)
# =============================================================================


@st.cache_data(ttl=3600)
def cargar_pyg() -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Carga pyg.parquet (Pérdidas y Ganancias) con metricas de calidad.

    Los datos de PYG tienen una estructura especial:
    - valor_acumulado: Valor acumulado en el año (como viene en el Excel)
    - valor_mes: Valor desacumulado del mes individual
    - valor_12m: Suma móvil de 12 meses (para comparabilidad)

    Returns:
        Tuple[DataFrame, Dict]: DataFrame y metricas de calidad
    """
    filepath = MASTER_DATA_DIR / "pyg.parquet"

    if not filepath.exists():
        raise FileNotFoundError(f"No se encontro {filepath}")

    df = pd.read_parquet(filepath)
    registros_originales = len(df)
    df = _categorizar_columnas(df, ['banco', 'codigo', 'cuenta'])

    # Filtrar cuentas vacias
    mask_cuenta_valida = _mascara_texto_valido(df['cuenta'])
    if not mask_cuenta_valida.all():
        df = df.loc[mask_cuenta_valida]

    # Filtrar valores nulos en columnas clave
    df = df.dropna(subset=['banco', 'fecha'])

    # Convertir fecha a datetime si no lo es
    if not pd.api.types.is_datetime64_any_dtype(df['fecha']):
        df['fecha'] = pd.to_datetime(df['fecha'])

    # Metricas de calidad
    calidad = {
        'registros_originales': registros_originales,
        'registros_limpios': len(df),
        'registros_eliminados': registros_originales - len(df),
        'pct_eliminados': round((registros_originales - len(df)) / registros_originales * 100, 2),
        'bancos': df['banco'].nunique(),
        'fechas': df['fecha'].nunique(),
        'fecha_min': df['fecha'].min(),
        'fecha_max': df['fecha'].max(),
        'cuentas_unicas': df['codigo'].nunique(),
        'registros_con_12m': df['valor_12m'].notna().sum(),
        'pct_con_12m': round(df['valor_12m'].notna().sum() / len(df) * 100, 1),
    }

    return df, calidad


@st.cache_data(ttl=3600)
def cargar_camel() -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Carga camel.parquet (Indicadores CAMEL) con metricas de calidad.

    Los datos de CAMEL incluyen indicadores financieros categorizados por:
    - C: Capital (solvencia)
    - A: Assets (activos, morosidad, cobertura)
    - M: Management (eficiencia operativa)
    - E: Earnings (rentabilidad)
    - L: Liquidity (liquidez)
    - Composicion Cartera (participacion por tipo de credito)

    Returns:
        Tuple[DataFrame, Dict]: DataFrame y metricas de calidad
    """
    filepath = MASTER_DATA_DIR / "camel.parquet"

    if not filepath.exists():
        raise FileNotFoundError(f"No se encontro {filepath}")

    df = pd.read_parquet(filepath)
    registros_originales = len(df)
    df = _categorizar_columnas(df, ['banco', 'codigo', 'indicador', 'categoria'])

    # Filtrar indicadores vacios
    mask_indicador_valido = _mascara_texto_valido(df['indicador'])
    if not mask_indicador_valido.all():
        df = df.loc[mask_indicador_valido]

    # Filtrar valores nulos en columnas clave
    df = df.dropna(subset=['banco', 'fecha'])

    # Convertir fecha a datetime si no lo es
    if not pd.api.types.is_datetime64_any_dtype(df['fecha']):
        df['fecha'] = pd.to_datetime(df['fecha'])

    # Metricas de calidad
    calidad = {
        'registros_originales': registros_originales,
        'registros_limpios': len(df),
        'registros_eliminados': registros_originales - len(df),
        'pct_eliminados': round((registros_originales - len(df)) / registros_originales * 100, 2),
        'bancos': df['banco'].nunique(),
        'fechas': df['fecha'].nunique(),
        'fecha_min': df['fecha'].min(),
        'fecha_max': df['fecha'].max(),
        'indicadores_unicos': df['codigo'].nunique(),
        'categorias': df['categoria'].unique().tolist(),
    }

    return df, calidad


@st.cache_data(ttl=3600)
def cargar_metadata() -> Dict[str, Any]:
    """
    Carga metadata.json con información de la última actualización.
    """
    filepath = MASTER_DATA_DIR / "metadata.json"

    if not filepath.exists():
        return {'error': 'metadata.json no encontrado'}

    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


@st.cache_data(ttl=3600)
def cargar_todos_los_datos() -> Dict[str, Any]:
    """
    Carga todos los datasets de una vez con sus metricas de calidad.

    Returns:
        Dict con DataFrames y metricas consolidadas
    """
    resultado = {
        'dataframes': {},
        'calidad': {},
        'metadata': None,
        'errores': []
    }

    # Cargar solo los 3 datasets esenciales
    try:
        df_balance, cal_balance = cargar_balance()
        resultado['dataframes']['balance'] = df_balance
        resultado['calidad']['balance'] = cal_balance
    except Exception as e:
        resultado['errores'].append(f"balance: {str(e)}")

    try:
        df_pyg, cal_pyg = cargar_pyg()
        resultado['dataframes']['pyg'] = df_pyg
        resultado['calidad']['pyg'] = cal_pyg
    except Exception as e:
        resultado['errores'].append(f"pyg: {str(e)}")

    try:
        df_camel, cal_camel = cargar_camel()
        resultado['dataframes']['camel'] = df_camel
        resultado['calidad']['camel'] = cal_camel
    except Exception as e:
        resultado['errores'].append(f"camel: {str(e)}")

    try:
        resultado['metadata'] = cargar_metadata()
    except Exception as e:
        resultado['errores'].append(f"metadata: {str(e)}")

    # Resumen consolidado
    if resultado['dataframes']:
        total_registros = sum(
            cal.get('registros_limpios', 0)
            for cal in resultado['calidad'].values()
        )
        resultado['resumen'] = {
            'total_registros': total_registros,
            'datasets_cargados': len(resultado['dataframes']),
            'errores_carga': len(resultado['errores']),
        }

    return resultado


def obtener_fechas_disponibles(df: pd.DataFrame) -> list:
    """
    Obtiene lista de fechas unicas ordenadas (mas reciente primero).
    """
    fechas = df['fecha'].dropna().unique()
    return sorted(fechas, reverse=True)


def obtener_bancos_disponibles(df: pd.DataFrame) -> list:
    """
    Obtiene lista de bancos unicos ordenados alfabeticamente.
    """
    return sorted(df['banco'].unique())


def filtrar_por_fecha(df: pd.DataFrame, fecha) -> pd.DataFrame:
    """
    Filtra DataFrame por fecha especifica.
    """
    return df[df['fecha'] == fecha].copy()


def filtrar_por_banco(df: pd.DataFrame, banco: str) -> pd.DataFrame:
    """
    Filtra DataFrame por banco especifico.
    """
    return df[df['banco'] == banco].copy()


def filtrar_por_codigo(df: pd.DataFrame, codigo: str) -> pd.DataFrame:
    """
    Filtra DataFrame por codigo contable.
    """
    return df[df['codigo'] == codigo].copy()


def obtener_valor_cuenta(
    df: pd.DataFrame,
    banco: str,
    fecha,
    codigo: str,
    hoja: str = 'BAL'
) -> float:
    """
    Obtiene el valor de una cuenta especifica para un banco y fecha.
    """
    mask = (
        (df['banco'] == banco) &
        (df['fecha'] == fecha) &
        (df['codigo'] == codigo) &
        (df['hoja'] == hoja)
    )
    resultado = df.loc[mask, 'valor']

    if resultado.empty:
        return None
    return resultado.iloc[0]
