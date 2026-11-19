"""No-Blender static smoke checks for the optional module."""
import ast
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class KitSmokeTests(unittest.TestCase):
    def test_blender_script_compiles_as_python(self):
        code = (ROOT / "blender" / "scenes" / "camera_exploded.py").read_text(encoding="utf-8")
        tree = ast.parse(code)
        names = {n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}
        self.assertTrue({"build_scene", "explode", "main"} <= names)
        self.assertIn("scene.frame_end = 720", code)

    def test_web_animation_is_local_only(self):
        html = (ROOT / "web" / "index.html").read_text(encoding="utf-8")
        self.assertIn("<canvas", html)
        self.assertIn("requestAnimationFrame", html)
        self.assertNotIn("<script src=", html)
        self.assertNotIn("fetch(", html)

    def test_installers_include_verified_sources(self):
        for file in ("scripts/install.sh", "scripts/install.ps1"):
            text = (ROOT / file).read_text(encoding="utf-8")
            self.assertIn("projects.blender.org/lab/blender_mcp.git", text)
            self.assertIn("mcp-for-blender", text)
            self.assertIn("codex mcp", text)

    def test_higgsfield_needs_login(self):
        doc = (ROOT / "docs" / "HIGGSFIELD.md").read_text(encoding="utf-8")
        self.assertIn("mcp.higgsfield.ai/mcp", doc)
        self.assertIn("yetkilendir", doc.lower())


if __name__ == "__main__":
    unittest.main()
