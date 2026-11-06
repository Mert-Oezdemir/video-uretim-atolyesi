"""Exercise the documented offline entry points with generated media."""

from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
import shutil
from tempfile import TemporaryDirectory
import unittest

from atolye.__main__ import main
from atolye.media import AtolyeError, job_path, read_json, require_tool, run, validate_srt, verify_video


class ValidationTests(unittest.TestCase):
    def test_relative_job_paths_cannot_leave_job(self):
        with TemporaryDirectory() as directory:
            with self.assertRaises(AtolyeError):
                job_path(Path(directory), "../other.mp4")

    def test_overlapping_or_out_of_bounds_srt_is_rejected(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "subtitle.srt"
            path.write_text(
                "1\n00:00:00,000 --> 00:00:01,000\nBir.\n\n"
                "2\n00:00:00,900 --> 00:00:02,000\nİki.\n",
                encoding="utf-8",
            )
            with self.assertRaises(AtolyeError):
                validate_srt(path, 2.0)
            path.write_text(
                "1\n00:00:00,000 --> 00:00:02,200\nBir.\n",
                encoding="utf-8",
            )
            with self.assertRaises(AtolyeError):
                validate_srt(path, 2.0)


@unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"), "FFmpeg ve ffprobe gerekli")
class OfflineWorkflowTest(unittest.TestCase):
    def run_cli(self, *args):
        output = StringIO()
        with redirect_stdout(output), redirect_stderr(output):
            result = main(list(args))
        self.assertEqual(result, 0, output.getvalue())

    def test_demo_builds_review_and_delivery_with_local_sources(self):
        with TemporaryDirectory() as directory:
            job = Path(directory) / "Türkçe örnek & test"
            self.run_cli("demo", str(job))
            self.run_cli("plan", str(job))
            self.run_cli("plan", str(job), "--stage", "storyboard")

            outputs = job / "outputs"
            package = outputs / "publish"
            report = read_json(package / "verification.json")
            self.assertAlmostEqual(report["duration"], 3.5, places=2)
            self.assertAlmostEqual(report["audio_duration"], report["duration"], places=2)
            self.assertEqual(report["captions"], 2)
            self.assertEqual(report["path"], "master.mp4")
            self.assertTrue((outputs / "preview.mp4").is_file())
            self.assertEqual((package / "master.mp4").read_bytes(), (outputs / "master.mp4").read_bytes())
            self.assertEqual((package / "captions.tr.srt").read_bytes(), (outputs / "master.srt").read_bytes())
            self.assertIn("https://ffmpeg.org/", (package / "description.txt").read_text(encoding="utf-8"))
            self.assertTrue((job / "plans" / "cut.prompt.md").is_file())
            self.assertTrue((job / "plans" / "storyboard.prompt.md").is_file())

    def test_voice_only_can_create_vertical_source(self):
        with TemporaryDirectory() as directory:
            job = Path(directory)
            self.run_cli("init", str(job))
            voice = job / "raw" / "voice.wav"
            run([require_tool("ffmpeg"), "-v", "error", "-f", "lavfi", "-i", "sine=duration=1.5", voice])
            self.run_cli("prepare", str(job), "--audio", "raw/voice.wav", "--aspect", "9:16")
            source = job / "raw" / "input.mp4"
            report = verify_video(source)
            self.assertEqual((report["width"], report["height"]), (720, 1280))
            self.assertAlmostEqual(report["duration"], 1.5, places=1)
            before = source.read_bytes()
            with redirect_stderr(StringIO()):
                self.assertEqual(main(["prepare", str(job), "--audio", "raw/voice.wav"]), 1)
            self.assertEqual(source.read_bytes(), before)

    @unittest.skipUnless(shutil.which("auto-editor"), "Auto-Editor isteğe bağlı")
    def test_auto_editor_removes_silence_from_real_media(self):
        with TemporaryDirectory() as directory:
            job = Path(directory)
            self.run_cli("init", str(job))
            voice = job / "raw" / "voice.wav"
            run([
                require_tool("ffmpeg"), "-v", "error", "-f", "lavfi", "-i",
                r"aevalsrc=if(between(t\,2\,4)\,0\,0.5*sin(2*PI*440*t)):s=48000:d=6",
                voice,
            ])
            self.run_cli("prepare", str(job), "--audio", "raw/voice.wav")
            self.run_cli("cut", str(job), "--auto")
            report = verify_video(job / "cut" / "locked.mp4")
            self.assertGreater(report["duration"], 4)
            self.assertLess(report["duration"], 5)


if __name__ == "__main__":
    unittest.main()
