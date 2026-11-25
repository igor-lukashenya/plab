import re
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
SKILLS = sorted(p.name for p in (ROOT / "skills").iterdir() if p.is_dir())


def frontmatter(path):
    _, fm, _ = path.read_text(encoding="utf-8").split("---\n", 2)
    return yaml.safe_load(fm)


class AgentDocsTests(unittest.TestCase):
    def test_agents_md_is_symlink_to_claude_md(self):
        agents = ROOT / "AGENTS.md"
        self.assertTrue(agents.is_symlink())
        self.assertEqual(agents.read_text(encoding="utf-8"), (ROOT / "CLAUDE.md").read_text(encoding="utf-8"))

    def test_skills_have_valid_frontmatter(self):
        self.assertTrue(SKILLS)
        for name in SKILLS:
            with self.subTest(skill=name):
                fm = frontmatter(ROOT / "skills" / name / "SKILL.md")
                self.assertEqual(fm["name"], name)
                self.assertTrue(str(fm["description"]).strip())

    def test_claude_skill_links_resolve(self):
        for name in SKILLS:
            with self.subTest(skill=name):
                self.assertTrue((ROOT / ".claude" / "skills" / name / "SKILL.md").exists())

    def test_make_targets_named_in_docs_exist(self):
        makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
        targets = set(re.findall(r"^([a-zA-Z0-9_-]+):", makefile, re.M))
        docs = [ROOT / "CLAUDE.md", ROOT / "README.md", ROOT / "media" / "README.md",
                ROOT / "notes" / "README.md", *sorted((ROOT / "skills").glob("*/SKILL.md"))]
        for doc in docs:
            with self.subTest(doc=doc.relative_to(ROOT).as_posix()):
                named = set(re.findall(r"make ([a-z][a-z0-9-]*)", doc.read_text(encoding="utf-8")))
                self.assertEqual(sorted(named - targets), [])
        self.assertTrue(set(re.findall(r"make ([a-z][a-z0-9-]*)", docs[0].read_text(encoding="utf-8"))))

    def test_workflows_parse(self):
        for name in ("ci.yml", "pages.yml"):
            with self.subTest(workflow=name):
                data = yaml.safe_load((ROOT / ".github" / "workflows" / name).read_text(encoding="utf-8"))
                self.assertIn("jobs", data)


if __name__ == "__main__":
    unittest.main()
