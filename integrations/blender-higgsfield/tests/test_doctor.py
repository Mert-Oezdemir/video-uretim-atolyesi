"""Doctor must not overclaim external connections."""
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("kitdoctor", ROOT / "scripts" / "doctor.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class DoctorTests(unittest.TestCase):
    def test_no_install_claim_from_static_paths(self):
        with patch.object(MODULE, "command_status", return_value={"status": "MISSING", "path": None, "version": None}):
            report = MODULE.inspect_local(ROOT)
        self.assertEqual(report["blender_mcp_live"]["status"], "NOT_VERIFIED")
        self.assertEqual(report["higgsfield_oauth"]["status"], "NOT_VERIFIED")
        self.assertFalse(report["ready_for_live_blender_mcp"])

    def test_nonexistent_command(self):
        with patch.object(MODULE.shutil, "which", return_value=None):
            status = MODULE.command_status("fake-cli")
        self.assertEqual(status["status"], "MISSING")

    def test_future_blender_version(self):
        def fake(name):
            version = "Blender 5.1.2" if name == "blender" else "v1.0"
            return {"status": "PASS", "path": "/bin/tool", "version": version}
        with patch.object(MODULE, "command_status", side_effect=fake):
            report = MODULE.inspect_local(ROOT)
        self.assertEqual(report["official_blender_version"]["status"], "PASS")
        self.assertEqual(report["blender_mcp_live"]["status"], "NOT_VERIFIED")


if __name__ == "__main__":
    unittest.main()
