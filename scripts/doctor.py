"""Check that the tools this repo needs are installed and print how to fix what is missing."""
import argparse
import glob
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHECK_NAMES = ("node", "python", "mkdocs", "npx", "hyperframes", "ffmpeg", "espeak-ng", "chrome-libs", "git-hooks")


@dataclass
class Check:
    name: str
    ok: bool
    required: bool
    fix: str


def _node_ok(env):
    node = shutil.which("node", path=env.get("PATH"))
    if not node:
        return False
    try:
        out = subprocess.run([node, "--version"], capture_output=True, text=True, timeout=10).stdout
    except (OSError, subprocess.SubprocessError):
        return False
    m = re.match(r"v(\d+)", out.strip())
    return bool(m) and int(m.group(1)) >= 22


def _mkdocs_ok(env):
    return (ROOT / ".venv" / "bin" / "mkdocs").exists() or bool(shutil.which("mkdocs", path=env.get("PATH")))


def _chrome_libs_ok(env):
    # Headless Chrome needs a few shared libraries; look for the usual ones in the linker cache.
    try:
        out = subprocess.run(["ldconfig", "-p"], capture_output=True, text=True, timeout=10).stdout
    except (OSError, subprocess.SubprocessError):
        out = ""
    if out:
        return all(lib in out for lib in ("libnss3", "libgbm", "libatk-1.0"))
    return bool(glob.glob("/usr/lib*/**/libnss3.so*", recursive=True))


def _hyperframes_ok(env):
    # The pinned version comes from the environment (make doctor passes HF_VERSION).
    version = env.get("HF_VERSION")
    npx = shutil.which("npx", path=env.get("PATH"))
    if not version or not npx:
        return False
    try:
        done = subprocess.run([npx, "--yes", f"hyperframes@{version}", "--version"],
                              capture_output=True, text=True, timeout=120)
    except (OSError, subprocess.SubprocessError):
        return False
    return done.returncode == 0


def _git_hooks_ok(env):
    try:
        out = subprocess.run(["git", "-C", str(ROOT), "config", "core.hooksPath"],
                             capture_output=True, text=True, timeout=10).stdout
    except (OSError, subprocess.SubprocessError):
        return False
    return out.strip() == ".githooks"


def default_probes(env):
    which = lambda tool: bool(shutil.which(tool, path=env.get("PATH")))  # noqa: E731
    return {
        "node": _node_ok(env),
        "python": sys.version_info >= (3, 0),
        "mkdocs": _mkdocs_ok(env),
        "npx": which("npx"),
        "hyperframes": _hyperframes_ok(env),
        "ffmpeg": which("ffmpeg"),
        "espeak-ng": which("espeak-ng"),
        "chrome-libs": _chrome_libs_ok(env),
        "git-hooks": _git_hooks_ok(env),
    }


# name, required, fix command
SPECS = (
    ("node", True, "install Node.js 22 or newer: https://nodejs.org"),
    ("python", True, "install Python 3: https://www.python.org"),
    ("mkdocs", True, "make install"),
    ("npx", True, "install Node.js 22 or newer (npx ships with it): https://nodejs.org"),
    ("hyperframes", True, "make slides-install"),
    ("ffmpeg", False, "make slides-deps"),
    ("espeak-ng", False, "make slides-deps"),
    ("chrome-libs", False, "make slides-deps"),
    ("git-hooks", False, "make hooks"),
)


def check(env=None, probes=None):
    """Return one Check per tool. `probes` maps check name to bool and replaces the real probes."""
    env = os.environ if env is None else env
    results = probes if probes is not None else default_probes(env)
    checks = [Check(name, bool(results.get(name, False)), required, fix) for name, required, fix in SPECS]
    if not env.get("HF_VERSION"):
        for c in checks:
            if c.name == "hyperframes" and not c.ok:
                c.fix = "HF_VERSION is not set: run this check through make doctor (it passes the pinned version)"
    return checks


def main(argv=None, probes=None):
    argparse.ArgumentParser(description=__doc__).parse_args(argv)
    failed_required = False
    for c in check(probes=probes):
        kind = "required" if c.required else "optional"
        if c.ok:
            print(f"[ok]      {c.name} ({kind})")
        else:
            print(f"[missing] {c.name} ({kind}): {c.fix}")
            failed_required = failed_required or c.required
    if failed_required:
        print("A required tool is missing.")
    return 1 if failed_required else 0


if __name__ == "__main__":
    raise SystemExit(main())
