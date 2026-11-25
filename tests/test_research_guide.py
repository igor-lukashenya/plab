import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

SECTIONS = [
    "## Quick checklist",
    "## 1. Frame first",
    "## 2. Note at checkpoints",
    "## 3. Keep sources",
    "## 4. Make runs reproducible",
    "## 5. Separate evidence from interpretation",
    "## 6. Close each case on purpose",
    "## 7. Review at the end",
]


def read(rel):
    return (ROOT / rel).read_text(encoding="utf-8")


class ResearchGuideTests(unittest.TestCase):
    def test_guide_has_all_sections(self):
        text = read("docs/how-to-research.md")
        for heading in SECTIONS:
            with self.subTest(heading=heading):
                self.assertIn(heading, text)

    def test_guide_in_nav(self):
        self.assertIn("how-to-research.md", read("mkdocs.yml"))

    def test_definition_points_to_guide(self):
        self.assertIn("how-to-research.md", read("docs/research-definition.md"))

    def test_readme_links_guide(self):
        self.assertIn("docs/how-to-research.md", read("README.md"))


if __name__ == "__main__":
    unittest.main()
