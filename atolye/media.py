"""Yerel medya işlemleri ve proje dosyalarının doğrulanması."""

import json
import math
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory


class AtolyeError(Exception):
    """Kullanıcıya gösterilecek işlem veya doğrulama hatası."""


def job_path(job: Path, relative: str | Path, *, must_exist: bool = False) -> Path:
    """Bir iş içindeki göreli yolu çöz ve kökten dışarı çıkmasını engelle."""
    job = job.resolve()
    relative = Path(relative)
    if relative.anchor or not relative.parts or ".." in relative.parts:
        raise AtolyeError(f"İş klasörüne göre bir dosya yolu bekleniyor: {relative}")
    local = job / relative
    path = local.resolve()
    if not path.is_relative_to(job) or path == job:
        raise AtolyeError(f"Yol iş klasörünün dışına çıkıyor: {relative}")
    if path != local:
        raise AtolyeError(f"Yönlendirilmiş yollar desteklenmiyor: {relative}")
    if must_exist and not path.is_file():
        raise AtolyeError(f"Dosya bulunamadı: {path}")
    return path


def read_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8-sig"))
    except (UnicodeError, ValueError) as exc:
        raise AtolyeError(f"JSON okunamadı: {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise AtolyeError(f"JSON kökü bir nesne olmalı: {path}")
    return value


def write_json(path: Path, data) -> None:
    write_text(path, json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False) + "\n")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix=".write-", dir=path.parent) as directory:
        staged = Path(directory) / path.name
        staged.write_text(content, encoding="utf-8", newline="\n")
        staged.replace(path)


def require_tool(tool: str) -> str:
    executable = shutil.which(tool)
    if executable is None:
        raise AtolyeError(f"{tool} PATH üzerinde bulunamadı. Kurulum için README'ye bakın.")
    return executable


def run(arguments: list[str | Path], *, cwd: Path | None = None) -> str:
    completed = subprocess.run(
        [str(part) for part in arguments], cwd=cwd, stdin=subprocess.DEVNULL,
        capture_output=True, encoding="utf-8", errors="replace", check=False,
        env={**os.environ, "PYTHONIOENCODING": "utf-8"},
    )
    if completed.returncode:
        detail = completed.stderr.strip() or completed.stdout.strip()
        raise AtolyeError(
            f"{Path(arguments[0]).name} başarısız oldu ({completed.returncode}).\n"
            f"{detail[-3000:]}"
        )
    return completed.stdout


def probe(path: Path) -> dict:
    return json.loads(run([
        require_tool("ffprobe"), "-v", "error", "-protocol_whitelist", "file,pipe",
        "-show_streams", "-show_format", "-of", "json", path,
    ]))


def stream(data: dict, kind: str) -> dict | None:
    return next(
        (item for item in data.get("streams", [])
         if item.get("codec_type") == kind and not item.get("disposition", {}).get("attached_pic")),
        None,
    )


def media_number(value) -> float:
    try:
        number = float(value)
        return number if math.isfinite(number) else 0.0
    except (TypeError, ValueError, OverflowError):
        return 0.0


def timeline_duration(data: dict, track: dict) -> float:
    return media_number(track.get("duration")) or media_number(data.get("format", {}).get("duration"))


def video_tracks(path: Path) -> tuple[dict, dict, dict]:
    data = probe(path)
    video, audio = stream(data, "video"), stream(data, "audio")
    if not video or not audio:
        raise AtolyeError(f"Video ve ses akışları gerekli: {path}")
    if timeline_duration(data, video) <= 0 or timeline_duration(data, audio) <= 0:
        raise AtolyeError(f"Medya süresi okunamadı: {path}")
    return data, video, audio


SRT_TIME = r"\d{2,}:[0-5]\d:[0-5]\d[,.]\d{3}"
SRT_CUE = re.compile(rf"({SRT_TIME})\s+-->\s+({SRT_TIME})")


def srt_seconds(timestamp: str) -> float:
    hours, minutes, seconds = timestamp.replace(",", ".").split(":")
    return int(hours) * 3600 + int(minutes) * 60 + float(seconds)


def validate_srt(path: Path, duration: float) -> int:
    content = path.read_text(encoding="utf-8-sig").strip()
    blocks = re.split(r"\n[ \t]*\n+", content) if content else []
    previous_end = 0.0
    for index, block in enumerate(blocks, start=1):
        lines = block.splitlines()
        match = SRT_CUE.fullmatch(lines[1].strip()) if len(lines) > 2 else None
        if match is None or not lines[0].strip().isdigit() or not "\n".join(lines[2:]).strip():
            raise AtolyeError(f"SRT {index}. satır grubu geçersiz: {path}")
        start_text, end_text = match.groups()
        start, end = srt_seconds(start_text), srt_seconds(end_text)
        if start < previous_end or end <= start or end > duration + 0.050:
            raise AtolyeError(f"SRT {index}. altyazı çakışıyor veya video sınırlarını aşıyor: {path}")
        previous_end = end
    return len(blocks)


def verify_video(path: Path, captions: Path | None = None) -> dict:
    data, video, audio = video_tracks(path)
    duration = timeline_duration(data, video)
    return {
        "path": str(path),
        "duration": duration,
        "video_codec": video.get("codec_name"),
        "width": video.get("width"),
        "height": video.get("height"),
        "fps": video.get("avg_frame_rate"),
        "audio_codec": audio.get("codec_name"),
        "audio_duration": timeline_duration(data, audio),
        "captions": validate_srt(captions, duration) if captions is not None else None,
    }


def positive_number(value, label: str, *, allow_zero: bool = False) -> float:
    if isinstance(value, bool) or not isinstance(value, (float, int)):
        raise AtolyeError(f"{label} sayısal ve sonlu olmalı.")
    number = media_number(value)
    if number < 0 or (number == 0 and (not allow_zero or value != 0)):
        raise AtolyeError(f"{label} için geçersiz değer: {value}")
    return number


def keep_ranges(path: Path, duration: float) -> list[tuple[float, float]]:
    entries = read_json(path).get("keep")
    if not isinstance(entries, list) or not entries:
        raise AtolyeError('Kesim planında boş olmayan bir "keep" dizisi gerekli.')
    spans = []
    previous_end = 0.0
    for index, item in enumerate(entries, start=1):
        if not isinstance(item, dict):
            raise AtolyeError(f"Kesim planında {index}. aralık nesne olmalı.")
        start = positive_number(item.get("start"), f"keep[{index}].start", allow_zero=True)
        end = positive_number(item.get("end"), f"keep[{index}].end")
        if start < previous_end or start >= end or end > duration:
            raise AtolyeError(f"Kesim aralığı sırasız, çakışıyor veya medya sınırı dışında: {start}–{end}.")
        spans.append((start, end))
        previous_end = end
    return spans


def _timestamp(seconds: float) -> str:
    minutes, within_minute = divmod(round(seconds * 1000), 60000)
    hours, minutes = divmod(minutes, 60)
    second, millis = divmod(within_minute, 1000)
    return f"{hours:02d}:{minutes:02d}:{second:02d},{millis:03d}"


def _normalized_transcript(data: dict, duration: float, language: str) -> dict:
    entries = data.get("segments")
    if not isinstance(entries, list):
        raise AtolyeError("Transkripsiyon sonucu segments dizisi içermiyor.")
    segments = []
    previous_end = 0.0
    for item in entries:
        if not isinstance(item, dict):
            raise AtolyeError("Geçersiz transkripsiyon bölümü.")
        text = " ".join(str(item.get("text", "")).split())
        start = round(max(previous_end, media_number(item.get("start"))), 3)
        end = round(min(duration, media_number(item.get("end"))), 3)
        if not text or end <= start:
            continue
        segment = {"start": start, "end": end, "text": text}
        if isinstance(item.get("words"), list):
            segment["words"] = item["words"]
        segments.append(segment)
        previous_end = end
    return {"language": data.get("language") or language, "segments": segments}


def transcribe(job: Path, relative: str, backend: str, name: str, language: str, model: str | None) -> Path:
    source = job_path(job, relative, must_exist=True)
    data = probe(source)
    audio = stream(data, "audio")
    if not audio:
        raise AtolyeError(f"Transkripsiyon için ses akışı gerekli: {source}")
    result_path = job_path(job, f"transcript/{name}.json")
    srt_path = job_path(job, f"transcript/{name}.srt")
    with TemporaryDirectory(prefix=".transcribe-", dir=job) as directory:
        staging = Path(directory)
        wave = staging / "voice.wav"
        run([
            require_tool("ffmpeg"), "-nostdin", "-hide_banner", "-loglevel", "error",
            "-protocol_whitelist", "file,pipe", "-i", source,
            "-map", f"0:{audio['index']}", "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le", wave,
        ])
        if backend == "mlx-whisper":
            run([
                require_tool("mlx_whisper"), wave, "--language", language,
                "--model", model or "mlx-community/whisper-small-mlx",
                "--output-dir", staging, "--output-format", "json", "--word-timestamps", "True",
            ])
        else:
            run([
                sys.executable, "-m", "whisper", wave, "--language", language, "--task", "transcribe",
                "--model", model or "small", "--output_dir", staging, "--output_format", "json",
                "--word_timestamps", "True",
            ])
        raw = read_json(staging / "voice.json")
        transcript = _normalized_transcript(raw, timeline_duration(data, audio), language)
        transcript.update(source=relative, backend=backend)
        srt = "\n\n".join(
            f"{index}\n{_timestamp(item['start'])} --> {_timestamp(item['end'])}\n{item['text']}"
            for index, item in enumerate(transcript["segments"], start=1)
        )
        write_json(result_path, transcript)
        write_text(srt_path, srt + "\n" if srt else "")
    return result_path


def video_encoding(ffmpeg: str, preview: bool = False) -> list[str]:
    encoders = run([ffmpeg, "-hide_banner", "-encoders"])
    if re.search(r"\blibx264\s", encoders):
        video = ["-c:v", "libx264", "-preset", "veryfast" if preview else "medium",
                 "-crf", "26" if preview else "18"]
    elif re.search(r"\blibopenh264\s", encoders):
        video = ["-c:v", "libopenh264", "-b:v", "2500k" if preview else "7000k"]
    else:
        raise AtolyeError("FFmpeg paketinde libx264 veya libopenh264 H.264 kodlayıcısı gerekli.")
    return [*video, "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart"]


def _ffmpeg_input(ffmpeg: str, source: Path) -> list[str | Path]:
    return [
        ffmpeg, "-nostdin", "-hide_banner", "-loglevel", "error", "-filter_complex_threads", "1",
        "-protocol_whitelist", "file,pipe", "-i", source,
    ]


def _even_dimensions(track: dict, preview: bool) -> tuple[int, int]:
    width = int(track["width"])
    height = int(track["height"])
    ratio = track.get("sample_aspect_ratio", "1:1").split(":")
    if len(ratio) == 2 and media_number(ratio[0]) > 0 and media_number(ratio[1]) > 0:
        width = round(width * float(ratio[0]) / float(ratio[1]))
    if any(abs(media_number(item.get("rotation"))) % 180 == 90 for item in track.get("side_data_list", [])):
        width, height = height, width
    scale = min(1.0, 1280 / width, 720 / height) if preview else 1.0
    return max(2, int(width * scale) // 2 * 2), max(2, int(height * scale) // 2 * 2)


def cut_video(job: Path, relative: str, plan: str | None, auto: bool) -> Path:
    source = job_path(job, relative, must_exist=True)
    target = job_path(job, "cut/locked.mp4")
    if source == target:
        raise AtolyeError("Kesim girdisi cut/locked.mp4 olamaz.")
    data, video, audio = video_tracks(source)
    spans = keep_ranges(job_path(job, plan, must_exist=True), timeline_duration(data, video)) if plan else []
    ffmpeg = require_tool("ffmpeg")
    width, height = _even_dimensions(video, preview=False)
    scale = f"scale={width}:{height},setsar=1"
    target.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix=".cut-", dir=target.parent) as directory:
        staging = Path(directory)
        draft = staging / "draft.mp4"
        arguments = _ffmpeg_input(ffmpeg, source)
        if spans:
            chains = []
            for index, (start, end) in enumerate(spans):
                chains.extend([
                    f"[0:{video['index']}]trim=start={start:.6f}:end={end:.6f},setpts=PTS-STARTPTS[v{index}]",
                    f"[0:{audio['index']}]atrim=start={start:.6f}:end={end:.6f},asetpts=PTS-STARTPTS[a{index}]",
                ])
            pads = "".join(f"[v{i}][a{i}]" for i in range(len(spans)))
            chains.extend([f"{pads}concat=n={len(spans)}:v=1:a=1[cv][a]", f"[cv]{scale}[v]"])
            arguments.extend(["-filter_complex", ";".join(chains), "-map", "[v]", "-map", "[a]"])
        else:
            arguments.extend(["-map", f"0:{video['index']}", "-map", f"0:{audio['index']}", "-vf", scale])
        run([*arguments, *video_encoding(ffmpeg), draft])
        if auto:
            tightened = staging / "tightened.mp4"
            run([require_tool("auto-editor"), draft, "--margin", "0.3s", "--no-open", "-o", tightened])
            draft = tightened
        verify_video(draft)
        draft.replace(target)
    return target


def _overlay_entries(job: Path, path: Path, duration: float) -> list[tuple[Path, float, float, dict]]:
    entries = read_json(path).get("overlays")
    if not isinstance(entries, list):
        raise AtolyeError('Grafik planında "overlays" dizisi gerekli.')
    result = []
    for index, item in enumerate(entries, start=1):
        if not isinstance(item, dict) or not isinstance(item.get("path"), str):
            raise AtolyeError(f"Grafik planında {index}. öğe path alanı içermeli.")
        path = job_path(job, item["path"], must_exist=True)
        start = positive_number(item.get("start"), f"overlays[{index}].start", allow_zero=True)
        length = positive_number(item.get("duration"), f"overlays[{index}].duration")
        overlay_data = probe(path)
        track = stream(overlay_data, "video")
        if not track or timeline_duration(overlay_data, track) + 0.050 < length:
            raise AtolyeError(f"Grafik klibi istenen süreden kısa veya video akışı yok: {path}")
        if start + length > duration + 0.000001:
            raise AtolyeError(f"Grafik onaylı kurgu süresini aşıyor: {path}")
        result.append((path, start, length, track))
    return result


def render_video(job: Path, relative: str, overlays: str | None, captions: str | None, *,
                 preview: bool, burn_in: bool) -> Path:
    if burn_in and not captions:
        raise AtolyeError("--burn-in için --captions gerekli.")
    source = job_path(job, relative, must_exist=True)
    stem = "preview" if preview else "master"
    target = job_path(job, f"outputs/{stem}.mp4")
    if source == target:
        raise AtolyeError("Render girdisi hedef MP4 ile aynı olamaz.")
    data, video, audio = video_tracks(source)
    duration = timeline_duration(data, video)
    entries = _overlay_entries(job, job_path(job, overlays, must_exist=True), duration) if overlays else []
    if any(path == target for path, _, _, _ in entries):
        raise AtolyeError("Render hedefi bir grafik girdisi olarak kullanılamaz.")
    caption_path = job_path(job, captions, must_exist=True) if captions else None
    srt_target = job_path(job, f"outputs/{stem}.srt")
    if caption_path is not None:
        validate_srt(caption_path, duration)
    width, height = _even_dimensions(video, preview)
    ffmpeg = require_tool("ffmpeg")
    arguments = _ffmpeg_input(ffmpeg, source)
    chains = [f"[0:{video['index']}]scale={width}:{height},setsar=1[v0]"]
    for index, (path, start, length, track) in enumerate(entries, start=1):
        if track.get("codec_name") == "vp9" and track.get("tags", {}).get("alpha_mode") == "1":
            arguments.extend(["-c:v", "libvpx-vp9"])
        arguments.extend(["-protocol_whitelist", "file,pipe", "-i", path])
        chains.extend([
            f"[{index}:{track['index']}]trim=duration={length:.6f},"
            f"setpts=PTS-STARTPTS+{start:.6f}/TB,"
            f"scale={width}:{height}:force_original_aspect_ratio=decrease,setsar=1,format=rgba[ov{index}]",
            f"[v{index-1}][ov{index}]overlay=x=(W-w)/2:y=(H-h)/2:"
            f"eof_action=pass:repeatlast=0:enable='gte(t,{start:.6f})*lt(t,{start+length:.6f})'[v{index}]",
        ])
    pad = f"[v{len(entries)}]"
    target.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix=".render-", dir=target.parent) as directory:
        staging = Path(directory)
        draft = staging / "video.mp4"
        staged_srt = staging / "captions.srt"
        if caption_path is not None:
            shutil.copyfile(caption_path, staged_srt)
        if burn_in:
            # A fixed relative filename avoids filter-expression escapes for Windows drive letters.
            chains.append(f"{pad}subtitles=captions.srt[subtitled]")
            pad = "[subtitled]"
        run([
            *arguments, "-filter_complex", ";".join(chains), "-map", pad, "-map", f"0:{audio['index']}",
            *video_encoding(ffmpeg, preview), draft,
        ], cwd=staging)
        verify_video(draft, staged_srt if caption_path is not None else None)
        draft.replace(target)
        if caption_path is not None:
            staged_srt.replace(srt_target)
        else:
            srt_target.unlink(missing_ok=True)
    return target
