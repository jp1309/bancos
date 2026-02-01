# ⚡ Guía Rápida - Descarga de Boletines

## 🚀 Descarga Inmediata (Primera Vez)

```bash
# 1. Instalar dependencias
pip install selenium requests webdriver-manager

# 2. Ejecutar (descarga Y descomprime automáticamente)
python descargar.py

# 3. Archivos Excel estarán en:
#    datos_bancos_diciembre_2025/archivos_excel/
```

## 📦 Solo Descomprimir (si ya tienes los ZIP)

```bash
python descomprimir_zips.py
```

## 🔄 Descargas Futuras (Enero 2026, Febrero 2026, etc.)

### Paso 1: Editar config.py

```python
# Cambiar estas dos líneas:
ANO_BUSCAR = "2026"              # Cambiar a 2026 cuando sea enero
PERIODO_DESCARGA = "enero_2026"  # Actualizar mes y año
```

### Paso 2: Ejecutar

```bash
python descargar.py
```

### Paso 3: Listo

Los archivos estarán en: `datos_bancos_enero_2026/archivos_excel/`

## ✅ Verificación Rápida

```bash
# Contar archivos descargados (debe mostrar 24)
ls datos_bancos_*/  | wc -l

# Ver tamaño total
du -sh datos_bancos_*/
```

## 🆘 Solución Rápida de Problemas

| Problema | Solución |
|----------|----------|
| No encuentra "Año 2026" | Editar `config.py`: `ANO_BUSCAR = "2026"` |
| No se descarga nada | Verificar que los archivos existan en el portal web |
| Error de ChromeDriver | `pip install --upgrade webdriver-manager` |
| Menos de 24 archivos | Normal si hubo fusiones de bancos |
| Archivos Excel iguales | ✅ Resuelto en v2.0 - Reinstalar script actualizado |

## 📋 Checklist Pre-Descarga

- [ ] ¿Actualizaste `ANO_BUSCAR` en `config.py`?
- [ ] ¿Actualizaste `PERIODO_DESCARGA` en `config.py`?
- [ ] ¿Tienes internet estable?
- [ ] ¿Instalaste las dependencias?

Si respondiste SÍ a todo: `python descargar.py` 🚀

## 📁 Estructura de Salida

```
datos_bancos_diciembre_2025/
├── Series Banco Amazonas DICIEMBRE 2025.zip
├── Series Banco Pichincha DICIEMBRE 2025.zip
├── ... (24 archivos ZIP)
└── archivos_excel/
    ├── Amazonas DICIEMBRE 2025/
    │   └── Amazonas DICIEMBRE 2025.xlsx
    ├── Pichincha DICIEMBRE 2025/
    │   └── Pichincha DICIEMBRE 2025.xlsx
    └── ... (24 carpetas con sus Excel)
```

## 💡 Tips

1. **Primera vez**: El navegador Chrome se abrirá automáticamente
2. **Tiempo**: La descarga completa toma 3-5 minutos
3. **Verificación**: Los archivos Excel deben tener tamaños diferentes (1.9 MB a 5.9 MB)
4. **Futuro**: Solo edita 2 líneas en `config.py` cada mes

## 📞 Más Ayuda

- **Documentación completa**: Ver [README.md](README.md)
- **Instrucciones detalladas**: Ver [INSTRUCCIONES_DESCARGA.md](INSTRUCCIONES_DESCARGA.md)
- **Portal web**: https://www.superbancos.gob.ec/estadisticas/portalestudios/bancos-2/

---

**Versión**: 2.0
**Última actualización**: 22 de enero de 2025
**Estado**: ✅ Funcional
