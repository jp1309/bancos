#!/usr/bin/env python3
"""Validaciones puras para los archivos publicados en el portal bancario."""

from __future__ import annotations

from urllib.parse import parse_qs, urlparse


HOST_PORTAL = "www.superbancos.gob.ec"
ACCION_DESCARGA = "shareonedrive-download"


def preparar_archivos_dom(archivos: list[dict]) -> list[dict]:
    """Normaliza y valida los enlaces observados en el DOM del portal oficial."""
    resultado = []
    for archivo in archivos:
        nombre = str(archivo.get("nombre", "")).strip()
        url = str(archivo.get("url", "")).strip()
        identificador = str(archivo.get("id", "")).strip()
        parsed = urlparse(url)
        query = parse_qs(parsed.query)

        if not nombre.lower().endswith(".zip"):
            raise ValueError(f"El portal anuncio un archivo no ZIP: {nombre!r}")
        if parsed.scheme != "https" or parsed.hostname != HOST_PORTAL:
            raise ValueError(f"Host de descarga no permitido para {nombre}: {parsed.hostname}")
        if query.get("action") != [ACCION_DESCARGA]:
            raise ValueError(f"Accion de descarga inesperada para {nombre}")
        if not identificador or query.get("id") != [identificador]:
            raise ValueError(f"Identificador inconsistente para {nombre}")

        resultado.append({"nombre": nombre, "url": url, "id": identificador})
    return resultado


def clasificar_publicacion(
    archivos: list[dict], periodo_objetivo: str, bancos_esperados: int
) -> str:
    """Distingue una publicacion objetivo, rezagada o parcial/inconsistente."""
    if len(archivos) != bancos_esperados:
        raise ValueError(
            f"Se esperaban {bancos_esperados} bancos y el portal mostro {len(archivos)}"
        )

    periodo = periodo_objetivo.upper()
    coincidentes = [a for a in archivos if periodo in a["nombre"].upper()]
    if len(coincidentes) == bancos_esperados:
        return "objetivo"
    if not coincidentes:
        return "rezagada"
    raise ValueError(
        f"Publicacion parcial: solo {len(coincidentes)} de {bancos_esperados} "
        f"archivos corresponden a {periodo_objetivo}"
    )
