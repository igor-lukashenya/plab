import importlib
import os
import sys
import tempfile
import unittest
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "media" / "shared"))

import engine  # noqa: E402


def make_project(tmp, fmt="deck"):
    """One-slide project at <tmp>/<fmt>/demo with a narration script and a short wav."""
    out = Path(tmp) / fmt / "demo"
    (out / "narration").mkdir(parents=True)
    (out / "assets" / "audio").mkdir(parents=True)
    (out / "narration" / "01-hello.txt").write_text("Hello there. This is the script.", encoding="utf-8")
    with wave.open(str(out / "assets" / "audio" / "01-hello.wav"), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(8000)
        w.writeframes(b"\x00\x00" * 8000 * 2)
    engine.slides.clear()
    engine.add("hello", "Intro", 5, '<div class="slide"><h1 class="a">Hello</h1></div>')
    return out


class EngineTest(unittest.TestCase):
    def read_all(self, out):
        text = (out / "index.html").read_text(encoding="utf-8")
        for f in sorted((out / "compositions").glob("*.html")):
            text += f.read_text(encoding="utf-8")
        return text

    def test_build_clean_has_no_caption_or_audio(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = make_project(tmp)
            engine.build(str(out))
            html = self.read_all(out)
            self.assertNotIn('class="captions"', html)
            self.assertNotIn("with-captions", html)
            self.assertNotIn("<audio", html)

    def test_build_with_captions_adds_caption_layer(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = make_project(tmp)
            engine.build(str(out), captions=True)
            html = self.read_all(out)
            self.assertIn('class="captions"', html)
            self.assertIn("with-captions", html)
            self.assertNotIn("<audio", html)

    def test_build_with_audio_adds_audio_element(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = make_project(tmp)
            engine.build(str(out), audio=True)
            html = self.read_all(out)
            self.assertIn("<audio", html)
            self.assertNotIn('class="captions"', html)

    def test_dimensions_follow_format_folder(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = make_project(tmp, "shorts")
            engine.build(str(out))
            html = (out / "index.html").read_text(encoding="utf-8")
            self.assertIn('data-width="1080"', html)
            self.assertIn('data-height="1920"', html)
            self.assertIn('data-format="shorts"', html)


if __name__ == "__main__":
    unittest.main()
