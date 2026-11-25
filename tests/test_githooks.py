import os
import shutil
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HOOKS = ("commit-msg", "pre-push")


def run(cwd, *args, env_extra=None):
    env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t",
               GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
    env.pop("SKIP_GITCHECK", None)
    env.update(env_extra or {})
    return subprocess.run(args, cwd=cwd, env=env, capture_output=True, text=True, timeout=60)


def make_repo(tmp, hooks=True):
    root = Path(tmp)
    run(root, "git", "init", "-q", "-b", "main")
    shutil.copytree(ROOT / "scripts", root / "scripts", ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copytree(ROOT / ".githooks", root / ".githooks")
    shutil.copy(ROOT / "Makefile", root / "Makefile")
    if hooks:
        run(root, "git", "config", "core.hooksPath", ".githooks")
    return root


class HookFilesTests(unittest.TestCase):
    def test_hooks_are_executable(self):
        for name in HOOKS:
            with self.subTest(hook=name):
                mode = (ROOT / ".githooks" / name).stat().st_mode
                self.assertTrue(mode & stat.S_IXUSR, f"{name} is not executable")


class CommitMsgHookTests(unittest.TestCase):
    def test_rejects_bad_message(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(tmp)
            r = run(root, "git", "commit", "-q", "--allow-empty", "-m", "added some stuff")
            self.assertNotEqual(r.returncode, 0)
            self.assertIn("not valid", r.stderr + r.stdout)

    def test_accepts_good_message(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(tmp)
            r = run(root, "git", "commit", "-q", "--allow-empty", "-m", "feat: add stuff")
            self.assertEqual(r.returncode, 0, r.stderr)

    def test_ignores_git_comment_lines(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(tmp)
            msg = root / "MSG"
            msg.write_text("# Please enter the commit message\nfix(scope): handle it\n# more\n", encoding="utf-8")
            r = run(root, ".githooks/commit-msg", str(msg))
            self.assertEqual(r.returncode, 0, r.stderr)

    def test_empty_message_file_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(tmp)
            msg = root / "MSG"
            msg.write_text("# only comments\n", encoding="utf-8")
            self.assertNotEqual(run(root, ".githooks/commit-msg", str(msg)).returncode, 0)

    def test_skip_env_allows_bad_message(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(tmp)
            r = run(root, "git", "commit", "-q", "--allow-empty", "-m", "added some stuff",
                    env_extra={"SKIP_GITCHECK": "1"})
            self.assertEqual(r.returncode, 0, r.stderr)

    def test_works_from_a_subdirectory(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(tmp)
            sub = root / "a" / "b"
            sub.mkdir(parents=True)
            r = run(sub, "git", "commit", "-q", "--allow-empty", "-m", "nope nope")
            self.assertNotEqual(r.returncode, 0)


class PrePushHookTests(unittest.TestCase):
    def test_rejects_bad_branch_name(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(tmp)
            run(root, "git", "commit", "-q", "--allow-empty", "-m", "feat: base")
            run(root, "git", "checkout", "-q", "-b", "wip")
            r = run(root, ".githooks/pre-push", "origin", "url")
            self.assertNotEqual(r.returncode, 0)
            self.assertIn("wip", r.stderr + r.stdout)

    def test_accepts_good_branch_and_main(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(tmp)
            run(root, "git", "commit", "-q", "--allow-empty", "-m", "feat: base")
            self.assertEqual(run(root, ".githooks/pre-push", "origin", "url").returncode, 0)
            run(root, "git", "checkout", "-q", "-b", "feat/thing")
            self.assertEqual(run(root, ".githooks/pre-push", "origin", "url").returncode, 0)

    def test_skip_env_allows_bad_branch(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(tmp)
            run(root, "git", "commit", "-q", "--allow-empty", "-m", "feat: base")
            run(root, "git", "checkout", "-q", "-b", "wip")
            r = run(root, ".githooks/pre-push", "origin", "url", env_extra={"SKIP_GITCHECK": "1"})
            self.assertEqual(r.returncode, 0, r.stderr)


@unittest.skipUnless(shutil.which("make"), "make not installed")
class MakeHooksTests(unittest.TestCase):
    def test_make_hooks_sets_hookspath(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(tmp, hooks=False)
            self.assertEqual(run(root, "git", "config", "core.hooksPath").stdout.strip(), "")
            r = run(root, "make", "--no-print-directory", "hooks")
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertEqual(run(root, "git", "config", "core.hooksPath").stdout.strip(), ".githooks")

    def test_make_hooks_outside_a_git_repo_explains_and_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            shutil.copy(ROOT / "Makefile", root / "Makefile")
            r = run(root, "make", "--no-print-directory", "hooks",
                    env_extra={"GIT_CEILING_DIRECTORIES": str(root.parent)})
            self.assertNotEqual(r.returncode, 0)
            self.assertIn("git", r.stderr + r.stdout)


if __name__ == "__main__":
    unittest.main()
