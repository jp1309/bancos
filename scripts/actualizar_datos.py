#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script maestro para actualización automática de datos.

Este script orquesta todo el proceso:
1. Verifica si hay nuevos datos disponibles
2. Descarga los datos del mes anterior
3. Procesa Balance, PyG y CAMEL
4. Actualiza los archivos parquet
5. Genera reporte de actualización

USO:
    python scripts/actualizar_datos.py

En GitHub Actions se ejecuta automáticamente el día 10 de cada mes.
"""

import os
import sys
import json
import shutil
import subprocess
from pathlib import Path
from datetime import datetime, timedelta

# Agregar directorio raíz al path
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(ROOT_DIR / "scripts"))

# Importar configuración
import config

# =============================================================================
# CONFIGURACIÓN
# =============================================================================

MASTER_DATA_DIR = ROOT_DIR / "master_data"
SCRIPTS_DIR = ROOT_DIR / "scripts"
STATUS_FILE = MASTER_DATA_DIR / "update_status.json"


def log(mensaje: str, nivel: str = "INFO"):
    """Imprime mensaje con timestamp."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        print(f"[{timestamp}] [{nivel}] {mensaje}")
    except UnicodeEncodeError:
        # Fallback para consolas Windows con encoding cp1252
        mensaje_ascii = mensaje.encode('ascii', errors='replace').decode('ascii')
        print(f"[{timestamp}] [{nivel}] {mensaje_ascii}")


def cargar_estado() -> dict:
    """Carga el estado de la última actualización."""
    if STATUS_FILE.exists():
        with open(STATUS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def guardar_estado(estado: dict):
    """Guarda el estado de actualización."""
    MASTER_DATA_DIR.mkdir(exist_ok=True)
    with open(STATUS_FILE, 'w', encoding='utf-8') as f:
        json.dump(estado, f, indent=2, ensure_ascii=False)


def verificar_datos_ya_actualizados() -> bool:
    """
    Verifica si los datos del mes objetivo ya fueron descargados.

    Returns:
        bool: True si ya están actualizados, False si necesita actualizar.
    """
    estado = cargar_estado()
    ultimo_periodo = estado.get('ultimo_periodo_descargado', '')

    periodo_actual = config.PERIODO_DESCARGA

    if ultimo_periodo == periodo_actual:
        log(f"Los datos de {periodo_actual} ya fueron descargados previamente")
        return True

    log(f"Datos pendientes de descargar: {periodo_actual}")
    return False


def ejecutar_script(script_name: str) -> bool:
    """
    Ejecuta un script Python y retorna si fue exitoso.

    Args:
        script_name: Nombre del script a ejecutar

    Returns:
        bool: True si el script se ejecutó correctamente
    """
    script_path = SCRIPTS_DIR / script_name
    log(f"Ejecutando: {script_name}")

    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=str(ROOT_DIR),
            capture_output=True,
            text=True,
            timeout=600  # 10 minutos máximo
        )

        if result.returncode == 0:
            log(f"[OK] {script_name} completado exitosamente")
            return True
        else:
            log(f"[FAIL] {script_name} fallo con codigo {result.returncode}", "ERROR")
            if result.stderr:
                log(f"  Error: {result.stderr[:500]}", "ERROR")
            return False

    except subprocess.TimeoutExpired:
        log(f"[FAIL] {script_name} excedio el tiempo limite", "ERROR")
        return False
    except Exception as e:
        log(f"[FAIL] Error ejecutando {script_name}: {e}", "ERROR")
        return False


def descargar_datos() -> bool:
    """
    Ejecuta el script de descarga.

    Returns:
        bool: True si la descarga fue exitosa
    """
    log("=" * 60)
    log("PASO 1: DESCARGA DE DATOS")
    log("=" * 60)

    return ejecutar_script("descargar.py")


def procesar_balance() -> bool:
    """Procesa los datos de Balance General."""
    log("=" * 60)
    log("PASO 2: PROCESAMIENTO DE BALANCE")
    log("=" * 60)

    return ejecutar_script("procesar_balance.py")


def procesar_pyg() -> bool:
    """Procesa los datos de Pérdidas y Ganancias."""
    log("=" * 60)
    log("PASO 3: PROCESAMIENTO DE P&G")
    log("=" * 60)

    return ejecutar_script("procesar_pyg.py")


def procesar_camel() -> bool:
    """Procesa los indicadores CAMEL."""
    log("=" * 60)
    log("PASO 4: PROCESAMIENTO DE CAMEL")
    log("=" * 60)

    return ejecutar_script("procesar_camel.py")


def verificar_archivos_generados() -> bool:
    """
    Verifica que se hayan generado los archivos parquet correctamente.

    Returns:
        bool: True si todos los archivos existen y tienen datos
    """
    log("=" * 60)
    log("PASO 5: VERIFICACIÓN DE ARCHIVOS")
    log("=" * 60)

    archivos_requeridos = [
        "balance.parquet",
        "pyg.parquet",
        "camel.parquet"
    ]

    todos_ok = True

    for archivo in archivos_requeridos:
        ruta = MASTER_DATA_DIR / archivo
        if ruta.exists():
            tamano_mb = ruta.stat().st_size / (1024 * 1024)
            log(f"  [OK] {archivo}: {tamano_mb:.2f} MB")
        else:
            log(f"  [FAIL] {archivo}: NO ENCONTRADO", "ERROR")
            todos_ok = False

    return todos_ok


def limpiar_datos_temporales():
    """Limpia archivos temporales de descarga."""
    log("Limpiando archivos temporales...")

    carpeta_descarga = ROOT_DIR / config.get_carpeta_salida()
    if carpeta_descarga.exists():
        try:
            shutil.rmtree(carpeta_descarga)
            log(f"  Eliminada carpeta: {carpeta_descarga.name}")
        except Exception as e:
            log(f"  No se pudo eliminar {carpeta_descarga.name}: {e}", "WARNING")


def generar_reporte(exitoso: bool, pasos_completados: list):
    """
    Genera un reporte de la actualización.

    Args:
        exitoso: Si la actualización fue exitosa
        pasos_completados: Lista de pasos completados
    """
    log("=" * 60)
    log("REPORTE DE ACTUALIZACIÓN")
    log("=" * 60)

    estado = {
        'fecha_ejecucion': datetime.now().isoformat(),
        'periodo_objetivo': config.PERIODO_DESCARGA,
        'exitoso': exitoso,
        'pasos_completados': pasos_completados,
    }

    if exitoso:
        estado['ultimo_periodo_descargado'] = config.PERIODO_DESCARGA
        log(f"[OK] ACTUALIZACION EXITOSA")
        log(f"  Periodo: {config.PERIODO_DESCARGA}")
    else:
        log(f"[FAIL] ACTUALIZACION FALLIDA", "ERROR")
        log(f"  Pasos completados: {pasos_completados}")

    guardar_estado(estado)

    return estado


def main():
    """Función principal de actualización."""
    log("=" * 60)
    log("INICIANDO ACTUALIZACIÓN AUTOMÁTICA DE DATOS")
    log("=" * 60)

    # Mostrar configuración
    config.mostrar_configuracion()

    # Verificar si ya está actualizado
    if verificar_datos_ya_actualizados():
        log("No es necesario actualizar. Saliendo.")
        return True

    pasos_completados = []
    exitoso = True

    # Paso 1: Descargar
    if descargar_datos():
        pasos_completados.append("descarga")
    else:
        log("La descarga falló. Verificando si es porque no hay datos disponibles aún...", "WARNING")
        # Guardar estado de intento fallido (para reintentar mañana)
        estado = cargar_estado()
        estado['ultimo_intento'] = datetime.now().isoformat()
        estado['ultimo_intento_periodo'] = config.PERIODO_DESCARGA
        estado['ultimo_intento_exitoso'] = False
        guardar_estado(estado)
        return False

    # Paso 2: Procesar Balance
    if procesar_balance():
        pasos_completados.append("balance")
    else:
        exitoso = False

    # Paso 3: Procesar PyG
    if procesar_pyg():
        pasos_completados.append("pyg")
    else:
        exitoso = False

    # Paso 4: Procesar CAMEL
    if procesar_camel():
        pasos_completados.append("camel")
    else:
        exitoso = False

    # Paso 5: Verificar archivos
    if verificar_archivos_generados():
        pasos_completados.append("verificacion")
    else:
        exitoso = False

    # Limpiar temporales solo si fue exitoso
    if exitoso:
        limpiar_datos_temporales()

    # Generar reporte
    generar_reporte(exitoso, pasos_completados)

    return exitoso


if __name__ == "__main__":
    try:
        exito = main()
        sys.exit(0 if exito else 1)
    except KeyboardInterrupt:
        log("Actualización cancelada por el usuario", "WARNING")
        sys.exit(1)
    except Exception as e:
        log(f"Error inesperado: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        sys.exit(1)
