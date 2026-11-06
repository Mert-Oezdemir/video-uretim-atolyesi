"""Video Üretim Atölyesi komut satırı."""

import argparse
import importlib.util
import json
import shutil
import sys
from pathlib import Path

from .media import (
    AtolyeError, cut_video, job_path, prepare_video, render_video, transcribe, verify_video, write_json, write_text,
)


def _init(args) -> None:
    for name in ("raw", "cut", "transcript", "graphics", "assets", "outputs"):
        job_path(args.job, name).mkdir(parents=True, exist_ok=True)
    brief = job_path(args.job, "brief.md")
    if not brief.exists():
        write_text(brief, "# Video özeti\n\n## İzleyici ve amaç\n\n## Çekim ve kurgu notları\n")
    overlays = job_path(args.job, "graphics/overlays.json")
    if not overlays.exists():
        write_json(overlays, {"overlays": []})
    print(args.job.resolve())


def _doctor(_args) -> None:
    required = ("ffmpeg", "ffprobe")
    for tool in (*required, "auto-editor", "mlx_whisper", "node", "npx", "codex", "claude"):
        status = shutil.which(tool) or ("eksik (gerekli)" if tool in required else "yok (isteğe bağlı)")
        print(f"{tool}: {status}")
    available = importlib.util.find_spec("whisper") is not None
    print(f"openai-whisper: {'kurulu' if available else 'yok (isteğe bağlı)'}")
    print(f"Python: {sys.version.split()[0]}")
    if any(shutil.which(tool) is None for tool in required):
        raise AtolyeError("FFmpeg ve ffprobe PATH üzerinde bulunmalı.")


def _transcribe(args) -> None:
    default = "raw/input.mp4" if args.name == "raw" else "cut/locked.mp4"
    print(transcribe(args.job, args.input or default, args.backend, args.name, args.language, args.model))


def _cut(args) -> None:
    print(cut_video(args.job, args.input, args.plan, args.auto))


def _prepare(args) -> None:
    print(prepare_video(args.job, args.audio, args.video, args.aspect))


def _render(args) -> None:
    print(render_video(
        args.job, args.input, args.overlays, args.captions, preview=args.preview, burn_in=args.burn_in,
    ))


def _verify(args) -> None:
    source = job_path(args.job, args.input, must_exist=True)
    captions = job_path(args.job, args.captions, must_exist=True) if args.captions else None
    print(json.dumps(verify_video(source, captions), ensure_ascii=False, indent=2))


def _add_job(subparsers, name, handler, help_text):
    parser = subparsers.add_parser(name, help=help_text)
    parser.add_argument("job", type=Path, help="Video işinin yerel klasörü")
    parser.set_defaults(func=handler)
    return parser


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m atolye", description="Yerel video üretim araçları.")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("doctor", help="Yerel araçları kontrol et").set_defaults(func=_doctor)
    _add_job(commands, "init", _init, "İş klasörünü hazırla")

    prepare = _add_job(commands, "prepare", _prepare, "Ayrı anlatım ve görüntüden kayıt tabanı oluştur")
    prepare.add_argument("--audio", required=True, help="İş klasörüne göre anlatım kaydı")
    prepare.add_argument("--video", help="İş klasörüne göre ekran veya tarayıcı kaydı")
    prepare.add_argument("--aspect", choices=("16:9", "9:16"), default="16:9")

    transcript = _add_job(commands, "transcribe", _transcribe, "Yerel Whisper ile JSON ve SRT üret")
    transcript.add_argument("--input", help="İş klasörüne göre ses veya video")
    transcript.add_argument("--backend", choices=("whisper", "mlx-whisper"), default="whisper")
    transcript.add_argument("--name", choices=("raw", "final"), default="raw")
    transcript.add_argument("--language", default="tr")
    transcript.add_argument("--model")

    cut = _add_job(commands, "cut", _cut, "Onaylı kaynak aralıklarından cut/locked.mp4 üret")
    cut.add_argument("--input", default="raw/input.mp4")
    cut.add_argument("--plan", help="İş klasörüne göre onaylı keep aralıkları JSON dosyası")
    cut.add_argument("--auto", action="store_true", help="Planın ardından Auto-Editor ile sessizlik kes")

    render = _add_job(commands, "render", _render, "MP4 önizleme veya ana kopya üret")
    render.add_argument("--input", default="cut/locked.mp4")
    render.add_argument("--overlays", help="İş klasörüne göre onaylı grafik planı JSON dosyası")
    render.add_argument("--captions", help="Onaylı kurgu zamanına ait SRT dosyası")
    render.add_argument("--burn-in", action="store_true", help="SRT'yi görüntüye de işle")
    render.add_argument("--preview", action="store_true", help="Hızlı önizleme üret")

    verify = _add_job(commands, "verify", _verify, "MP4 akışlarını ve isteğe bağlı SRT'yi doğrula")
    verify.add_argument("--input", default="outputs/master.mp4")
    verify.add_argument("--captions", help="İş klasörüne göre SRT dosyası")

    from . import editorial

    editorial.register(commands)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        args.func(args)
    except (AtolyeError, OSError, ValueError) as exc:
        print(f"Hata: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
