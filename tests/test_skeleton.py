import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class SkeletonTest(unittest.TestCase):
    def test_nav_marker_present(self):
        text = (ROOT / "mkdocs.yml").read_text()
        self.assertEqual(text.count("# new-case:insert"), 1)

    def test_makefile_pins(self):
        text = (ROOT / "Makefile").read_text()
        self.assertIn("HF_VERSION ?= 0.8.138", text)
        self.assertIn("SLIDES_VENV := $(abspath media/.venv)", text)


if __name__ == "__main__":
    unittest.main()
