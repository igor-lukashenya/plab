import io
import sys
import os
import unittest
from contextlib import redirect_stdout
from unittest import mock
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import doctor  # noqa: E402

ALL_OK = {name: True for name in doctor.CHECK_NAMES}


def run_main(probes):
    out = io.StringIO()
    with redirect_stdout(out), mock.patch.dict(os.environ, {"HF_VERSION": "0.0.0-test"}):
        code = doctor.main([], probes=probes)
    return code, out.getvalue()


class DoctorTests(unittest.TestCase):
    def test_check_returns_all_checks(self):
        results = doctor.check(probes=ALL_OK)
        self.assertEqual([c.name for c in results], list(doctor.CHECK_NAMES))
        self.assertTrue(all(c.ok for c in results))

    def test_doctor_reports_missing_required_and_exits_nonzero(self):
        code, out = run_main({**ALL_OK, "mkdocs": False, "node": False})
        self.assertNotEqual(code, 0)
        self.assertIn("mkdocs", out)
        self.assertIn("make install", out)

    def test_doctor_optional_missing_does_not_fail(self):
        code, out = run_main({**ALL_OK, "ffmpeg": False, "espeak-ng": False, "chrome-libs": False})
        self.assertEqual(code, 0)
        self.assertIn("ffmpeg", out)
        self.assertIn("make slides-deps", out)

    def test_missing_hyperframes_fails_with_fix(self):
        code, out = run_main({**ALL_OK, "hyperframes": False})
        self.assertNotEqual(code, 0)
        self.assertIn("hyperframes", out)
        self.assertIn("make slides-install", out)

    def test_hyperframes_ok_passes(self):
        code, out = run_main(ALL_OK)
        self.assertEqual(code, 0)
        self.assertIn("[ok]      hyperframes (required)", out)

    def test_hyperframes_unset_version_is_clear(self):
        results = doctor.check(env={}, probes={**ALL_OK, "hyperframes": False})
        hf = next(c for c in results if c.name == "hyperframes")
        self.assertFalse(hf.ok)
        self.assertIn("HF_VERSION", hf.fix)

    def test_required_flags(self):
        required = {c.name for c in doctor.check(probes=ALL_OK) if c.required}
        self.assertEqual(required, {"node", "python", "mkdocs", "npx", "hyperframes"})


if __name__ == "__main__":
    unittest.main()
