"""Offline tests of official-community Autodesk URL parsing."""
import importlib.util
from pathlib import Path
import unittest

SOURCE = Path(__file__).resolve().parents[1] / "scripts" / "discover-autocad.py"
spec = importlib.util.spec_from_file_location("discover_autocad", SOURCE)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

BASE = "https://efulfillment.autodesk.com/NetSWDLD/ODIS/prd/2027/ACDMAC/DA13C2BB-9635-3AD7-9E72-CB16D8C17DB6/SFX/Autodesk_AutoCAD_2027.1_macOS.dmg"

class TestDiscovery(unittest.TestCase):
    def test_accept_public_dmg(self):
        self.assertEqual(mod.candidate(BASE)["version"], "2027.1")

    def test_reject_session_token_and_wrong_host(self):
        self.assertIsNone(mod.candidate(BASE + "?session_id=secret"))
        self.assertIsNone(mod.candidate(BASE.replace("autodesk.com", "example.com")))

    def test_reject_other_products(self):
        self.assertIsNone(mod.candidate(BASE.replace("/ACDMAC/", "/ACDLTM/")))

    def test_deduplicate_and_sort(self):
        old = BASE.replace("2027.1_macOS", "2027_macOS")
        html = '<a href="' + old + '">old</a><a href="' + BASE + '">new</a><a href="' + BASE + '">again</a>'
        result = mod.discover(html)
        self.assertEqual([x["version"] for x in result], ["2027.1", "2027"])

if __name__ == "__main__":
    unittest.main()
