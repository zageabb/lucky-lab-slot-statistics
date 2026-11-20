"""No-network, no-database regression coverage for Lucky Lab start/maintenance split."""
from __future__ import annotations

import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
START = ROOT / "docker-entrypoint.sh"
MAINTAIN = ROOT / "scripts" / "lucky-lab-db-maintenance.sh"


class TestDbLifecycle(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="lucky-uda-v2-")
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.bin = self.directory / "bin"
        self.bin.mkdir()
        self.log = self.directory / "calls.txt"
        for command in ("flask", "gunicorn"):
            executable = self.bin / command
            executable.write_text(
                "#!/bin/sh\necho " + command + " \"$*\" >> \"$TEST_LOG\"\n"
            )
            executable.chmod(0o700)
        self.env = {
            **os.environ,
            "PATH": str(self.bin) + os.pathsep + os.environ.get("PATH", ""),
            "TEST_LOG": str(self.log),
            "LUCKY_LAB_DATA_DIR": str(self.directory / "data"),
            "DATABASE_URL": "sqlite:////isolated-fixture-only.db",
        }
        for name in ("LUCKY_LAB_DB_MAINTENANCE_APPROVED",
                     "LUCKY_LAB_DB_BACKUP_VERIFIED",
                     "LUCKY_LAB_DB_TARGET_CONFIRMED"):
            self.env.pop(name, None)

    def run_script(self, script, *args, **flags):
        env = {**self.env, **flags}
        return subprocess.run(
            ["sh", str(script), *args], cwd=ROOT, env=env,
            check=False, capture_output=True, text=True, timeout=10,
        )

    def calls(self):
        return self.log.read_text() if self.log.exists() else ""

    def test_web_start_never_invokes_flask_db_or_seed(self):
        p = self.run_script(START)
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertIn("gunicorn", self.calls())
        self.assertNotIn("flask", self.calls())

    def test_maintenance_denied_by_default(self):
        for operation in ("upgrade", "seed"):
            p = self.run_script(MAINTAIN, operation)
            self.assertEqual(p.returncode, 3)
        self.assertEqual(self.calls(), "")

    def test_requires_every_approval_and_database_target(self):
        flags = {
            "LUCKY_LAB_DB_MAINTENANCE_APPROVED": "yes",
            "LUCKY_LAB_DB_BACKUP_VERIFIED": "yes",
            "LUCKY_LAB_DB_TARGET_CONFIRMED": "yes",
        }
        for missing in flags:
            case = {**flags, missing: "no"}
            self.assertEqual(self.run_script(MAINTAIN, "upgrade", **case).returncode, 3)
        self.assertEqual(self.calls(), "")

    def test_rejects_unrecognised_operation(self):
        p = self.run_script(MAINTAIN, "upgrade-and-seed")
        self.assertEqual(p.returncode, 2)
        self.assertEqual(self.calls(), "")

    def test_explicit_approved_operations_are_separate(self):
        flags = {
            "LUCKY_LAB_DB_MAINTENANCE_APPROVED": "yes",
            "LUCKY_LAB_DB_BACKUP_VERIFIED": "yes",
            "LUCKY_LAB_DB_TARGET_CONFIRMED": "yes",
        }
        self.assertEqual(self.run_script(MAINTAIN, "upgrade", **flags).returncode, 0)
        self.assertIn("flask --app app:create_app db upgrade", self.calls())
        self.assertNotIn("main seed", self.calls())
        self.log.unlink()
        self.assertEqual(self.run_script(MAINTAIN, "seed", **flags).returncode, 0)
        self.assertIn("flask --app app:create_app main seed", self.calls())
        self.assertNotIn("db upgrade", self.calls())


if __name__ == "__main__":
    unittest.main()
