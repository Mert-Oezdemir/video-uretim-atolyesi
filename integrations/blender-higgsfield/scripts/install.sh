#!/usr/bin/env bash
set -euo pipefail
BACKEND=official
if [[ $# -gt 0 ]]; then BACKEND="$1"; fi
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
if [[ "$BACKEND" != official && "$BACKEND" != community ]]; then
  echo "Kullanım: bash scripts/install.sh [official|community]" >&2; exit 2
fi
command -v git >/dev/null || { echo "Git kurmalısın." >&2; exit 1; }
command -v uv >/dev/null || { echo "uv kurmalısın: https://docs.astral.sh/uv/" >&2; exit 1; }
if [[ "$BACKEND" == official ]]; then
  mkdir -p "$ROOT/vendor"
  if [[ ! -d "$ROOT/vendor/blender_mcp/.git" ]]; then
    git clone https://projects.blender.org/lab/blender_mcp.git "$ROOT/vendor/blender_mcp"
  else
    echo "Kaynak önceden mevcut, otomatik git pull yapılmadı."
  fi
  SERVER_DIR="$ROOT/vendor/blender_mcp/mcp"
  [[ -d "$SERVER_DIR" ]] || { echo "Sunucu bulunamadı: $SERVER_DIR" >&2; exit 1; }
else
  uvx mcp-for-blender install-addon
fi
if command -v codex >/dev/null; then
  if codex mcp list 2>/dev/null | grep -Eq '^[[:space:]]*blender[[:space:]]'; then
    echo "Codex blender MCP girişi var, üzerine yazılmadı."
    echo "Değiştirmek için önce: codex mcp remove blender"
  elif [[ "$BACKEND" == official ]]; then
    codex mcp add blender -- uv --directory "$SERVER_DIR" run blender-mcp
  else
    codex mcp add blender -- uvx mcp-for-blender
  fi
  codex mcp list
else
  echo "Codex henüz kurulu değil; kurduktan sonra:"
  if [[ "$BACKEND" == official ]]; then
    printf 'codex mcp add blender -- uv --directory "%s" run blender-mcp\n' "$SERVER_DIR"
  else
    echo "codex mcp add blender -- uvx mcp-for-blender"
  fi
fi
if [[ "$BACKEND" == official ]]; then
  echo "Blender 5.1+ içinden MCP add-on kur: https://www.blender.org/lab/mcp-server/"
else
  echo "Blender'da N → MCP for Blender panelini kontrol et."
fi
echo "Kurulum komutları tamam. Bağlantı için Blender'ı aç."
