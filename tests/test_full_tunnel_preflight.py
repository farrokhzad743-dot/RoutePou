import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from windows.full_tunnel_preflight import run_preflight

class PreflightTests(unittest.TestCase):
    def test_missing_runtime_is_not_ready(self):
        with tempfile.TemporaryDirectory() as d:
            result = run_preflight(d)
        self.assertFalse(result["preflight_ready"])
        self.assertFalse(result["data_plane_verified"])
        self.assertTrue(any(not c["ok"] for c in result["checks"]))

    def test_runtime_files_are_detected(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "relaywg-client.exe").write_bytes(b"placeholder")
            (root / "wintun.dll").write_bytes(b"placeholder")
            with patch("windows.full_tunnel_preflight._is_windows", return_value=True), \
                 patch("windows.full_tunnel_preflight.is_admin", return_value=True), \
                 patch("windows.full_tunnel_preflight.shutil.which", return_value="wg.exe"), \
                 patch("windows.full_tunnel_preflight._run", return_value=(True, "Ethernet")):
                result = run_preflight(root)
        names = {c["name"]: c["ok"] for c in result["checks"]}
        self.assertTrue(names["wireguard_worker"])
        self.assertTrue(names["wintun_runtime"])
        self.assertTrue(names["administrator"])
        self.assertFalse(result["data_plane_verified"])

    def test_result_is_json_serializable(self):
        self.assertIsInstance(json.dumps(run_preflight()), str)

if __name__ == "__main__":
    unittest.main()
