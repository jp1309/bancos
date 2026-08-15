import unittest
import tempfile
import importlib.util
from pathlib import Path
from unittest.mock import patch

from dashboard_metadata import resumir_metadata


DATA_LOADER_PATH = Path(__file__).parent.parent / "utils" / "data_loader.py"
SPEC = importlib.util.spec_from_file_location("data_loader_under_test", DATA_LOADER_PATH)
data_loader = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(data_loader)


class DashboardMetadataTests(unittest.TestCase):
    def test_resume_portada_desde_metadata_publicada(self):
        resumen = resumir_metadata({
            "fecha_min": "2003-01-31 00:00:00",
            "fecha_max": "2026-06-30 00:00:00",
            "total_bancos": 23,
            "total_registros": 8_152_043,
        })

        self.assertTrue(resumen["completa"])
        self.assertEqual(resumen["bancos"], 23)
        self.assertEqual(resumen["meses"], 282)
        self.assertEqual(resumen["anos"], 23)
        self.assertEqual(resumen["datos_al"], "Jun 2026")
        self.assertEqual(resumen["periodo"], "Enero 2003 - Junio 2026")
        self.assertEqual(resumen["registros"], "8,2 millones")

    def test_no_inventa_cifras_si_falta_metadata(self):
        resumen = resumir_metadata(None)

        self.assertFalse(resumen["completa"])
        self.assertEqual(resumen["bancos"], "N/D")
        self.assertEqual(resumen["datos_al"], "N/D")

    def test_cache_balance_recibe_huella_del_parquet(self):
        with tempfile.TemporaryDirectory() as tmp:
            directorio = Path(tmp)
            parquet = directorio / "balance.parquet"
            parquet.write_bytes(b"version-1")
            original = data_loader.MASTER_DATA_DIR
            data_loader.MASTER_DATA_DIR = directorio
            self.addCleanup(setattr, data_loader, "MASTER_DATA_DIR", original)

            with patch.object(
                data_loader, "_cargar_balance_cache", return_value=(None, {})
            ) as cache:
                data_loader.cargar_balance()

            cache.assert_called_once_with(
                str(parquet), data_loader._huella_archivo(parquet)
            )


if __name__ == "__main__":
    unittest.main()
