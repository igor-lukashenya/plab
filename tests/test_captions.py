import re
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "media" / "shared"))

import captions  # noqa: E402
import engine  # noqa: E402

TS = re.compile(r"(\d\d):(\d\d):(\d\d),(\d{3}) --> (\d\d):(\d\d):(\d\d),(\d{3})")


def narration(tmp, files):
    d = Path(tmp) / "narration"
    d.mkdir()
    for name, text in files.items():
        (d / f"{name}.txt").write_text(text, encoding="utf-8")
    return d


def stamps(path):
    out = []
    for m in TS.finditer(path.read_text(encoding="utf-8")):
        g = [int(x) for x in m.groups()]
        out.append((g[0] * 3600 + g[1] * 60 + g[2] + g[3] / 1000, g[4] * 3600 + g[5] * 60 + g[6] + g[7] / 1000))
    return out


class CaptionsTest(unittest.TestCase):
    def test_srt_has_monotonic_timestamps(self):
        with tempfile.TemporaryDirectory() as tmp:
            n = narration(tmp, {"01-a": "One. Two, three, four. " * 6 + "End!"})
            [srt] = captions.write_srt(n, {"01-a": 12.345}, Path(tmp) / "out")
            pairs = stamps(srt)
            self.assertGreater(len(pairs), 1)
            prev_end = 0.0
            for a, b in pairs:
                self.assertGreaterEqual(a, prev_end)
                self.assertGreater(b, a)
                prev_end = b
            self.assertAlmostEqual(prev_end, 12.345, places=2)

    def test_srt_one_file_per_narration(self):
        with tempfile.TemporaryDirectory() as tmp:
            n = narration(tmp, {"01-a": "Hello there.", "02-b": "Second one."})
            out = Path(tmp) / "out"
            paths = captions.write_srt(n, {"01-a": 3.0, "02-b": 4.0}, out)
            self.assertEqual([p.name for p in paths], ["01-a.srt", "02-b.srt"])
            self.assertEqual(sorted(p.name for p in out.iterdir()), ["01-a.srt", "02-b.srt"])

    def test_no_narration_means_no_srt_and_no_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            self.assertEqual(captions.write_srt(Path(tmp) / "missing", {}, out), [])
            empty = Path(tmp) / "narration"
            empty.mkdir()
            self.assertEqual(captions.write_srt(empty, {}, out), [])
            self.assertFalse(out.exists())

    def test_srt_round_trips_through_engine_parse_srt(self):
        with tempfile.TemporaryDirectory() as tmp:
            text = "First sentence here. Second, with a comma, and more words to split."
            n = narration(tmp, {"01-a": text})
            [srt] = captions.write_srt(n, {"01-a": 7.5}, Path(tmp) / "out")
            parsed = engine.parse_srt(str(srt))
            expected = engine.derive_cues(text, 7.5)
            self.assertEqual([c[2] for c in parsed], [c[2] for c in expected])
            for (a, b, _), (ea, eb, _) in zip(parsed, expected):
                self.assertAlmostEqual(a, ea, places=2)
                self.assertAlmostEqual(b, eb, places=2)

    def test_missing_duration_falls_back_to_script_estimate(self):
        with tempfile.TemporaryDirectory() as tmp:
            n = narration(tmp, {"01-a": "word " * 18})
            [srt] = captions.write_srt(n, {}, Path(tmp) / "out")
            self.assertAlmostEqual(stamps(srt)[-1][1], 18 / engine.WORDS_PER_SEC, places=2)

    def test_sidecar_is_offset_by_slide_start_and_lead(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "deck" / "demo"
            (out / "narration").mkdir(parents=True)
            (out / "narration" / "01-a.txt").write_text("First slide words here.", encoding="utf-8")
            (out / "narration" / "02-b.txt").write_text("Second slide words here.", encoding="utf-8")
            engine.slides.clear()
            engine.add("a", "", 5, '<div class="slide"></div>')
            engine.add("b", "", 5, '<div class="slide"></div>')
            engine.build(str(out), notes=False)
            target = out / "renders" / "demo.srt"
            captions.write_sidecar(out, target)
            pairs = stamps(target)
            second_start = captions.slide_starts(out)["02-b"]
            self.assertGreater(second_start, 0)
            self.assertAlmostEqual(pairs[0][0], engine.LEAD, places=2)
            self.assertAlmostEqual(pairs[-1][0], second_start + engine.LEAD, places=2)
            self.assertTrue(all(b > a for a, b in pairs))


if __name__ == "__main__":
    unittest.main()
