import re
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
UNTRUSTED = ("github.head_ref", "github.base_ref", "pull_request.title")


def workflow():
    return yaml.safe_load((ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8"))


class ConventionsJobTests(unittest.TestCase):
    def setUp(self):
        self.job = workflow()["jobs"]["conventions"]

    def test_runs_only_on_pull_requests(self):
        self.assertIn("pull_request", self.job["if"])

    def test_checkout_has_full_history(self):
        checkout = next(s for s in self.job["steps"] if str(s.get("uses", "")).startswith("actions/checkout"))
        self.assertEqual(checkout["with"]["fetch-depth"], 0)

    def test_untrusted_values_only_reach_the_shell_through_env(self):
        env = {}
        for step in self.job["steps"]:
            env.update(step.get("env", {}))
            run = step.get("run", "")
            for needle in UNTRUSTED:
                self.assertNotIn(needle, run, f"{needle} interpolated into a run: block")
        self.assertIn("github.head_ref", env["HEAD_REF"])
        self.assertIn("pull_request.title", env["PR_TITLE"])
        self.assertIn("github.base_ref", env["BASE_REF"])

    def test_checks_branch_title_and_commits_with_quoted_variables(self):
        run = "\n".join(s.get("run", "") for s in self.job["steps"])
        self.assertIn('gitcheck.py branch "$HEAD_REF"', run)
        self.assertIn('gitcheck.py title "$PR_TITLE"', run)
        self.assertIn('gitcheck.py commits "origin/$BASE_REF..HEAD"', run)

    def test_existing_test_job_is_untouched(self):
        self.assertIn("test", workflow()["jobs"])
        wf = workflow()
        triggers = wf.get("on", wf.get(True))  # PyYAML reads a bare `on:` key as True
        self.assertEqual(sorted(triggers), ["pull_request", "push"])


class GitConventionDocsTests(unittest.TestCase):
    def test_claude_md_documents_the_rules_for_agents(self):
        text = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
        self.assertIn("## Git conventions", text)
        for needle in ("make hooks", "--no-verify", "feat/", "Conventional Commits", "never commit on `main`"):
            self.assertIn(needle, text)

    def test_readme_documents_conventions_and_hooks(self):
        text = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertRegex(text, re.compile(r"^## Git conventions$", re.M))
        self.assertIn("make hooks", text)
        self.assertIn("ruleset", text)


if __name__ == "__main__":
    unittest.main()
