import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import gitcheck  # noqa: E402


def git(cwd, *args):
    env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t",
               GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
    env.pop("SKIP_GITCHECK", None)
    return subprocess.run(["git", *args], cwd=cwd, env=env, check=True,
                          capture_output=True, text=True).stdout.strip()


class BranchTests(unittest.TestCase):
    def test_branch_valid(self):
        for name in ["main", "feat/note-search", "fix/123-init-marker", "docs/readme"]:
            gitcheck.check_branch(name)

    def test_branch_invalid(self):
        bad = ["feature/x", "feat/Note", "feat/", "feat/" + "a" * 51, "Main",
               "feat/a--b", "wip", "feat/-a", "feat/a-", "feat/a_b"]
        for name in bad:
            with self.subTest(name=name), self.assertRaises(SystemExit):
                gitcheck.check_branch(name)

    def test_branch_description_limit_is_50(self):
        gitcheck.check_branch("feat/" + "a" * 50)

    def test_error_message_includes_rule_and_example(self):
        with self.assertRaises(SystemExit) as cm:
            gitcheck.check_branch("wip")
        text = str(cm.exception)
        self.assertIn("wip", text)
        self.assertIn("Expected", text)
        self.assertIn("feat/", text)


class HeaderTests(unittest.TestCase):
    def test_header_valid(self):
        for h in ["feat: add x", "fix(scope)!: y", "feat(a/b): c", "chore(deps.dev): d",
                  "feat!: breaking"]:
            with self.subTest(h=h):
                gitcheck.check_header(h)

    def test_header_invalid(self):
        for h in ["Feat: x", "feat:x", "feat: ", "feat: x.", "feat(): x", "foo: x",
                  "feat(Scope): x", "just text", ""]:
            with self.subTest(h=h), self.assertRaises(SystemExit):
                gitcheck.check_header(h)

    def test_header_length_limit_is_72(self):
        ok = "feat: " + "a" * (72 - len("feat: "))
        self.assertEqual(len(ok), 72)
        gitcheck.check_header(ok)
        with self.assertRaises(SystemExit) as cm:
            gitcheck.check_header(ok + "a")
        self.assertIn("73", str(cm.exception))

    def test_special_headers_pass(self):
        for h in ["Merge branch 'x'", "Merge pull request #1 from a/b", 'Revert "feat: x"',
                  "fixup! feat: x", "squash! fix: y", "amend! fix: z"]:
            with self.subTest(h=h):
                gitcheck.check_header(h)


class MessageTests(unittest.TestCase):
    def test_message_ignores_comments_and_blank_lines(self):
        gitcheck.check_message("\n# comment\n\nfeat: add x\n\nbody line\n# Please enter\n")

    def test_message_empty_or_only_comments_fails(self):
        for text in ["", "\n\n", "# only a comment\n# another\n"]:
            with self.subTest(text=text), self.assertRaises(SystemExit):
                gitcheck.check_message(text)

    def test_message_checks_first_real_line(self):
        with self.assertRaises(SystemExit):
            gitcheck.check_message("# c\nadded stuff\n")


class CliTests(unittest.TestCase):
    def test_skip_env_bypasses_all_subcommands(self):
        with mock.patch.dict(os.environ, {"SKIP_GITCHECK": "1"}):
            gitcheck.main(["branch", "wip"])
            gitcheck.main(["message", "bad message"])
            gitcheck.main(["title", "bad title"])
            gitcheck.main(["commits", "nope..nope"])

    def test_title_uses_header_rule(self):
        gitcheck.main(["title", "feat: add thing"])
        with self.assertRaises(SystemExit):
            gitcheck.main(["title", "Add thing"])

    def test_message_reads_a_file_when_the_path_exists(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "MSG"
            p.write_text("# c\nfeat: ok\n", encoding="utf-8")
            gitcheck.main(["message", str(p)])
            p.write_text("nope\n", encoding="utf-8")
            with self.assertRaises(SystemExit):
                gitcheck.main(["message", str(p)])


class RepoTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = self.tmp.name
        git(self.repo, "init", "-q", "-b", "main")
        git(self.repo, "config", "core.hooksPath", "/dev/null")

    def tearDown(self):
        self.tmp.cleanup()

    def test_branch_default_in_new_repo_without_commits_passes(self):
        cwd = os.getcwd()
        os.chdir(self.repo)
        try:
            gitcheck.main(["branch"])
        finally:
            os.chdir(cwd)

    def test_branch_default_uses_current_branch(self):
        git(self.repo, "commit", "-q", "--allow-empty", "-m", "feat: first")
        git(self.repo, "checkout", "-q", "-b", "wip")
        cwd = os.getcwd()
        os.chdir(self.repo)
        try:
            with self.assertRaises(SystemExit):
                gitcheck.main(["branch"])
        finally:
            os.chdir(cwd)

    def test_detached_head_passes(self):
        git(self.repo, "commit", "-q", "--allow-empty", "-m", "feat: first")
        git(self.repo, "checkout", "-q", "--detach")
        cwd = os.getcwd()
        os.chdir(self.repo)
        try:
            gitcheck.main(["branch"])
        finally:
            os.chdir(cwd)

    def test_commits_over_temp_repo_names_the_bad_header(self):
        git(self.repo, "commit", "-q", "--allow-empty", "-m", "feat: base")
        base = git(self.repo, "rev-parse", "HEAD")
        git(self.repo, "commit", "-q", "--allow-empty", "-m", "feat: good one")
        git(self.repo, "commit", "-q", "--allow-empty", "-m", "bad header here")
        with self.assertRaises(SystemExit) as cm:
            gitcheck.check_commits(Path(self.repo), f"{base}..HEAD")
        self.assertIn("bad header here", str(cm.exception))

    def test_commits_counts_good_range(self):
        git(self.repo, "commit", "-q", "--allow-empty", "-m", "feat: base")
        base = git(self.repo, "rev-parse", "HEAD")
        git(self.repo, "commit", "-q", "--allow-empty", "-m", "fix: one")
        git(self.repo, "commit", "-q", "--allow-empty", "-m", "docs(readme): two")
        self.assertEqual(gitcheck.check_commits(Path(self.repo), f"{base}..HEAD"), 2)


if __name__ == "__main__":
    unittest.main()
