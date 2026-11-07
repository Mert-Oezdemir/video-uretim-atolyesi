"""Preserve the reviewed workflow inputs between preview and delivery."""

import hashlib
import importlib.util
import os
from contextlib import contextmanager
from pathlib import Path

from .media import AtolyeError, job_path, read_json, require_tool, write_json


@contextmanager
def job_lock(job: Path):
    job = job.resolve()
    if not job.is_dir():
        raise AtolyeError("Önce init ile iş klasörünü oluştur.")
    path = job_path(job, ".workflow.lock")
    try:
        handle = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as error:
        raise AtolyeError(
            "Bu iş için bir üretim zaten çalışıyor. Önceki işlem çöktüyse çalışmadığını "
            "doğrulayıp iş klasöründeki .workflow.lock dosyasını kaldır."
        ) from error
    try:
        with os.fdopen(handle, "w", encoding="utf-8") as lock:
            lock.write(str(os.getpid()))
        yield
    finally:
        path.unlink(missing_ok=True)


def fingerprint(path: Path) -> str:
    checksum = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            checksum.update(block)
    return checksum.hexdigest()


def inputs(args) -> dict:
    paths = [args.input]
    if args.plan:
        paths.append(args.plan)
    if args.overlays:
        paths.append(args.overlays)
        entries = read_json(job_path(args.job, args.overlays, must_exist=True)).get("overlays")
        if not isinstance(entries, list):
            raise AtolyeError("Grafik planı overlays listesi içermeli.")
        for entry in entries:
            if not isinstance(entry, dict) or not isinstance(entry.get("path"), str):
                raise AtolyeError("Grafik satırında path gerekli.")
            paths.append(entry["path"])
    return {
        "files": {path: fingerprint(job_path(args.job, path, must_exist=True)) for path in paths},
        "options": {
            name: getattr(args, name)
            for name in ("input", "plan", "keep_all", "auto", "backend", "language", "model", "overlays", "burn_in")
        },
    }


def preflight(args) -> dict:
    require_tool("ffmpeg")
    require_tool("ffprobe")
    snapshot = inputs(args)
    if not args.final:
        if args.backend == "whisper" and importlib.util.find_spec("whisper") is None:
            raise AtolyeError("Bu Python ortamında openai-whisper yok. Whisper kurulu ortamın python komutunu kullan.")
        if args.backend == "mlx-whisper":
            require_tool("mlx_whisper")
        if args.auto:
            require_tool("auto-editor")
    return snapshot


def save_preview(args, snapshot: dict) -> None:
    if inputs(args) != snapshot:
        raise AtolyeError("Üretim sırasında girdiler değişti. Sabit girdilerle yeniden önizleme üret.")
    snapshot["generated"] = {
        name: fingerprint(job_path(args.job, name, must_exist=True))
        for name in ("cut/locked.mp4", "transcript/final.json", "transcript/final.srt", "outputs/preview.mp4")
    }
    write_json(job_path(args.job, "outputs/workflow-preview.json"), snapshot)


def require_preview(args, snapshot: dict) -> None:
    path = job_path(args.job, "outputs/workflow-preview.json")
    if not path.is_file():
        raise AtolyeError("Önce aynı ayarlarla --final olmadan önizleme üret ve incele.")
    previous = read_json(path)
    if previous.get("files") != snapshot["files"] or previous.get("options") != snapshot["options"]:
        raise AtolyeError("Önizlemeden sonra girdi veya ayarlar değişmiş. Yeni önizleme üret.")
    generated = previous.get("generated")
    expected = {"cut/locked.mp4", "transcript/final.json", "transcript/final.srt", "outputs/preview.mp4"}
    if not isinstance(generated, dict) or set(generated) != expected:
        raise AtolyeError("Önizleme kaydı eksik. Yeni önizleme üret.")
    if any(fingerprint(job_path(args.job, name, must_exist=True)) != digest for name, digest in generated.items()):
        raise AtolyeError("Önizleme dosyaları değiştirilmiş. Yeni önizleme üret.")
