"""Offline tests for the local AutoCAD cask generator."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

SOURCE = Path(__file__).resolve().parents[1] / "scripts" / "prepare-autocad-cask.py"
spec = importlib.util.spec_from_file_location("prepare_autocad", SOURCE)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class TestAutoCADCask(unittest.TestCase):
    def test_sha256(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "test.dmg"
            path.write_bytes(b"autocad-test")
            self.assertEqual(
                module.digest(path),
                "0fef1d8d57080571b903149e1db6f324ddd2a05a3b8467f4ba969567dd7360f5"
            )

    def test_renders_local_uri_and_checksum(self):
        dmg = Path("/tmp/Autodesk AutoCAD 2027.dmg")
        cask = module.render(dmg, 2027, "Install AutoCAD.app/Contents/Helper/Setup.app/Contents/MacOS/Setup", "a" * 64)
        self.assertIn('sha256 "' + "a" * 64 + '"', cask)
        self.assertIn('file:///tmp/Autodesk%20AutoCAD%202027.dmg', cask)
        self.assertIn('args:       ["--silent"]', cask)
        self.assertIn('sudo:       true', cask)
        self.assertNotIn("token=", cask)


if __name__ == "__main__":
    unittest.main()
