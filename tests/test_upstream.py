import importlib.util
import pathlib
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("upstream", ROOT / "scripts/check-upstream.py")
upstream = importlib.util.module_from_spec(spec)
spec.loader.exec_module(upstream)


class ManifestTests(unittest.TestCase):
    def manifest(self, filename=None, digest=None):
        filename = filename or "appdmg_osx.zip." + "a" * 40
        digest = digest or "b" * 64
        return ('"osx" { "version" "123" "appdmg_osx" { '
                '"steamchina" { "file" "wrong" "sha2" "wrong" } '
                f'"file" "{filename}" "sha2" "{digest}" }} }}')

    def test_selects_default_not_china(self):
        self.assertEqual(upstream.parse_manifest(self.manifest())["file"], "appdmg_osx.zip." + "a" * 40)

    def test_rejects_paths_and_invalid_hashes(self):
        for filename, digest in [("../evil", "b" * 64), (None, "bad")]:
            with self.assertRaises(ValueError):
                upstream.parse_manifest(self.manifest(filename, digest))

    def test_rejects_truncated_and_duplicate(self):
        for text in [self.manifest()[:-1], self.manifest().replace('"version" "123"', '"version" "123" "version" "456"')]:
            with self.assertRaises(ValueError):
                upstream.parse_manifest(text)

    def test_bad_checksum_fails_before_extraction(self):
        with tempfile.TemporaryDirectory() as directory:
            path = pathlib.Path(directory)
            archive = path / "bad.zip"
            archive.write_bytes(b"broken download")
            with self.assertRaisesRegex(ValueError, "SHA-256 mismatch"):
                upstream.verify({"sha256": "0" * 64}, archive, path)
            self.assertEqual(list(path.iterdir()), [archive])


if __name__ == "__main__":
    unittest.main()
