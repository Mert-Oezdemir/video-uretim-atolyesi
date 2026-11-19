#!/usr/bin/env python3
"""Read-only, offline preflight. Never claims MCP/OAuth connections work.

Usage:
    python scripts/doctor.py
    python scripts/doctor.py --json
    python scripts/doctor.py --json --strict
"""
import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ("python", "git", "uv", "uvx", "codex", "blender", "ffmpeg", "ffprobe")


def command_status(name):
    path = shutil.which(name)
    if not path:
        return {"status": "MISSING", "path": None, "version": None}
    try:
        result = subprocess.run(
            [path, "--version"],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, encoding="utf-8", errors="replace",
            timeout=5, check=False,
        )
        lines = (result.stdout or "").splitlines()
        version = lines[0].strip()[:220] if lines else None
        status = "PASS" if result.returncode == 0 else "NOT_VERIFIED"
    except (subprocess.SubprocessError, OSError) as exc:
        status, version = "NOT_VERIFIED", type(exc).__name__
    return {"status": status, "path": path, "version": version}


def inspect_local(root=ROOT):
    commands = {name: command_status(name) for name in TOOLS}
    official = root / "vendor" / "blender_mcp" / "mcp" / "pyproject.toml"
    installed = official.is_file()
    diagnostics = {
        "checks": commands,
        "blender_lab_source": {
            "status": "PRESENT" if installed else "NOT_INSTALLED",
            "path": str(official),
        },
        "blender_addon": {
            "status": "NOT_VERIFIED",
            "reason": "Add-on state must be checked inside Blender UI and by a live read-only MCP call.",
        },
        "blender_mcp_live": {
            "status": "NOT_VERIFIED",
            "reason": "CLI config is not a live connection check.",
        },
        "higgsfield_oauth": {
            "status": "NOT_VERIFIED",
            "reason": "Account sign-in requires user interaction and a read-only connected tool check.",
        },
        "higgsfield_credits": {
            "status": "NOT_VERIFIED",
            "reason": "Never infer balances or make paid generation calls.",
        },
        "blender_script": {
            "status": "PRESENT" if (root / "blender/scenes/camera_exploded.py").is_file() else "MISSING"
        },
        "web_example": {
            "status": "PRESENT" if (root / "web/index.html").is_file() else "MISSING"
        },
    }
    text = commands["blender"].get("version") or ""
    match = re.search(r"Blender\s+(\d+)\.(\d+)", text)
    if match:
        major, minor = (int(v) for v in match.groups())
        diagnostics["official_blender_version"] = {
            "status": "PASS" if (major, minor) >= (5, 1) else "UNSUPPORTED",
            "detected": f"{major}.{minor}",
            "required": "5.1+ for official Blender Lab MCP",
        }
    else:
        diagnostics["official_blender_version"] = {
            "status": "NOT_VERIFIED", "required": "5.1+ for official Blender Lab MCP"
        }
    diagnostics["ready_for_live_blender_mcp"] = False
    diagnostics["note"] = (
        "This offline doctor NEVER validates a Blender MCP connection. "
        "Start Blender and verify by a read-only tool call."
    )
    return diagnostics


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    parser.add_argument("--strict", action="store_true", help="exit nonzero if required CLIs are absent")
    args = parser.parse_args()
    result = inspect_local()
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        for name, details in result["checks"].items():
            print(f"{name:8} {details['status']:13} {details['version'] or '-'}")
        print("Blender add-on / MCP live / Higgsfield OAuth: NOT_VERIFIED (needs user or live client)")
    required = ("python", "git", "uv", "codex", "blender")
    bad = [name for name in required if result["checks"][name]["status"] != "PASS"]
    if result["official_blender_version"]["status"] == "UNSUPPORTED":
        bad.append("Blender 5.1+")
    return 1 if args.strict and bad else 0


if __name__ == "__main__":
    sys.exit(main())
