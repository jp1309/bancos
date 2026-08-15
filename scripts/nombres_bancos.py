#!/usr/bin/env python3
"""Identidad estable y nombres de presentacion para bancos privados."""

from __future__ import annotations

import re
import unicodedata


NOMBRES_CANONICOS = (
    "Amazonas",
    "Atlantida",
    "Austro",
    "Bolivariano",
    "Capital",
    "Citibank",
    "Codesarrollo",
    "Comercial de Manabí",
    "Coopnacional",
    "DelBank",
    "Diners",
    "General Rumiñahui",
    "Guayaquil",
    "Internacional",
    "Litoral",
    "Loja",
    "Machala",
    "Pacífico",
    "Pichincha",
    "Procredit",
    "Produbanco",
    "Solidario",
    "VisionFund",
)


def clave_banco(nombre: str) -> str:
    """Crea una clave que tolera mayusculas, espacios y variantes Unicode."""
    texto = unicodedata.normalize("NFKD", str(nombre))
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", texto).strip().casefold()


_POR_CLAVE = {clave_banco(nombre): nombre for nombre in NOMBRES_CANONICOS}


def normalizar_banco(nombre: str) -> str:
    """Devuelve el nombre canonico conocido o, si es nuevo, Unicode NFC limpio."""
    limpio = re.sub(r"\s+", " ", unicodedata.normalize("NFC", str(nombre))).strip()
    return _POR_CLAVE.get(clave_banco(limpio), limpio)
