"""Build an offline HyperFrames composition from a single JSON scene."""

import argparse
from html import escape
import json
import math
from pathlib import Path
import re
import shutil
from urllib.parse import urlsplit


ASPECTS = {"16:9": (1920, 1080), "9:16": (1080, 1920)}
DIFF_MARKERS = {"add": "+", "remove": "−", "context": " "}
FONT_FORMATS = {".woff2": "woff2", ".woff": "woff", ".ttf": "truetype"}


def field(record, key, limit, *, required=True):
    value = record.get(key, "")
    if not isinstance(value, str):
        raise ValueError(f"'{key}' metin olmalı.")
    value = value.strip()
    if required and not value:
        raise ValueError(f"'{key}' boş olamaz.")
    if len(value) > limit:
        raise ValueError(f"'{key}' alanı en fazla {limit} karakter olmalı.")
    return escape(value)


def group(record, key):
    value = record.get(key)
    if not isinstance(value, dict):
        raise ValueError(f"'{key}' bir JSON nesnesi olmalı.")
    return value


def entries(record, key, low, high):
    value = record.get(key)
    if not isinstance(value, list) or not low <= len(value) <= high:
        raise ValueError(f"'{key}' alanında {low}–{high} öğe olmalı.")
    if not all(isinstance(entry, dict) for entry in value):
        raise ValueError(f"'{key}' öğeleri JSON nesneleri olmalı.")
    return value


def comparison(scene):
    cards = []
    for key, fallback in (("before", "Önce"), ("after", "Sonra")):
        item = group(scene, key)
        label = field(item, "label", 28, required=False) or fallback
        value = field(item, "value", 28)
        detail = field(item, "detail", 95, required=False)
        cards.append(f'''<section class="comparison-card {key}">
          <p class="eyebrow">{label}</p>
          <p class="metric">{value}</p>
          <p class="detail">{detail}</p>
        </section>''')
    return '<div class="comparison">' + "\n".join(cards) + '</div>'


def code_diff(scene):
    filename = field(scene, "filename", 60)
    lines = []
    for item in entries(scene, "lines", 1, 8):
        kind = item.get("kind")
        if not isinstance(kind, str) or kind not in DIFF_MARKERS:
            raise ValueError("Diff türü add, remove veya context olmalı.")
        content = item.get("text")
        if not isinstance(content, str) or len(content) > 90 or "\r" in content or "\n" in content:
            raise ValueError("Diff metni tek satır ve en fazla 90 karakter olmalı.")
        lines.append(f'''<div class="line {kind}"><b>{DIFF_MARKERS[kind]}</b>
          <code>{escape(content)}</code></div>''')
    return f'''<section class="code-card">
      <p class="eyebrow filename">{filename}</p>
      <div class="diff">{''.join(lines)}</div>
    </section>'''


def architecture(scene):
    cards = []
    for index, item in enumerate(entries(scene, "steps", 2, 4), start=1):
        label = field(item, "label", 38)
        detail = field(item, "detail", 58, required=False)
        cards.append(f'''<li class="flow-card">
          <span class="step">{index:02d}</span><div><strong>{label}</strong>
          <p class="detail">{detail}</p></div>
        </li>''')
    return '<ol class="flow">' + "\n".join(cards) + '</ol>'


def source_card(scene):
    source = group(scene, "source")
    name = field(source, "name", 75)
    url = field(source, "url", 200)
    parsed = urlsplit(source["url"].strip())
    if parsed.scheme not in {"https", "http"} or not parsed.hostname or parsed.username is not None:
        raise ValueError("Kaynak URL'si geçerli bir HTTP(S) adresi olmalı.")
    note = field(source, "note", 155, required=False)
    return f'''<section class="source-card">
      <p class="eyebrow">KAYNAK</p>
      <p class="source-name">{name}</p>
      <p class="source-url">{url}</p>
      <p class="detail">{note}</p>
    </section>'''


TEMPLATES = {
    "before-after": comparison,
    "code-diff": code_diff,
    "architecture": architecture,
    "source-card": source_card,
}


def composition(scene, aspect, transparent, accent, font_css):
    if not isinstance(scene, dict):
        raise ValueError("Sahne girdisi bir JSON nesnesi olmalı.")
    kind = scene.get("type")
    if not isinstance(kind, str) or kind not in TEMPLATES:
        raise ValueError("Sahne türü: " + ", ".join(TEMPLATES))
    duration = scene.get("duration")
    if type(duration) not in (float, int) or not 1 <= duration <= 30 or not math.isfinite(duration):
        raise ValueError("'duration' saniye cinsinden 1–30 arası bir sayı olmalı.")
    title = field(scene, "title", 82)
    subtitle = field(scene, "subtitle", 135, required=False)
    eyebrow = field(scene, "eyebrow", 30, required=False) or "VİDEO ÜRETİM ATÖLYESİ"
    width, height = ASPECTS[aspect]
    direction = "portrait" if aspect == "9:16" else "landscape"
    backdrop = "transparent" if transparent else "#101a23"
    stylesheet = Path(__file__).with_name("style.css").read_text(encoding="utf-8")
    content = TEMPLATES[kind](scene)
    summary = f'<p class="summary">{subtitle}</p>' if subtitle else ""
    return f'''<!doctype html>
<html lang="tr">
<head>
  <meta charset="utf-8">
  <title>{title}</title>
  <style>
    :root {{ --scene-width: {width}px; --scene-height: {height}px;
      --backdrop: {backdrop}; --accent: {accent}; }}
    {stylesheet}
    {font_css}
  </style>
</head>
<body>
  <main id="atolye" class="{direction}" data-composition-id="atolye"
        data-width="{width}" data-height="{height}" data-start="0"
        data-duration="{duration}" data-fps="30" data-no-timeline>
    <article class="board">
      <header>
        <p class="eyebrow kicker">{eyebrow}</p>
        <h1>{title}</h1>
        {summary}
      </header>
      {content}
    </article>
  </main>
</body>
</html>
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scene", type=Path, help="Sahne JSON dosyası")
    parser.add_argument("output", type=Path, help="HyperFrames proje klasörü")
    parser.add_argument("--aspect", choices=ASPECTS, default="16:9")
    parser.add_argument("--transparent", action="store_true", help="Pano dışında alfa bırak")
    parser.add_argument("--accent", default="#bcf0bc", help="Açık vurgu rengi (#RRGGBB)")
    parser.add_argument("--font", type=Path, help="İsteğe bağlı yerel .woff2, .woff veya .ttf")
    args = parser.parse_args()

    try:
        if not re.fullmatch(r"#[0-9a-fA-F]{6}", args.accent):
            raise ValueError("'--accent' #RRGGBB biçiminde olmalı.")
        scene = json.loads(args.scene.read_text(encoding="utf-8-sig"))
        font_css = ""
        if args.font:
            suffix = args.font.suffix.lower()
            if suffix not in FONT_FORMATS or not args.font.is_file():
                raise ValueError("Yerel .woff2, .woff veya .ttf dosyası gerekli.")
            font_name = "atolye-font" + suffix
            font_css = (
                f'@font-face {{ font-family: Atolye; src: url("./{font_name}") '
                f'format("{FONT_FORMATS[suffix]}"); font-display: swap; }}'
                '\nbody { font-family: Atolye, "Segoe UI", Arial, sans-serif; }'
            )
        html = composition(scene, args.aspect, args.transparent, args.accent, font_css)
        args.output.mkdir(parents=True, exist_ok=True)
        if args.font:
            target = args.output / font_name
            if args.font.resolve() != target.resolve():
                shutil.copyfile(args.font, target)
        output = args.output / "index.html"
        output.write_text(html, encoding="utf-8")
    except (ValueError, OSError) as error:
        parser.exit(2, f"Hata: {error}\n")

    print(output)


if __name__ == "__main__":
    main()
