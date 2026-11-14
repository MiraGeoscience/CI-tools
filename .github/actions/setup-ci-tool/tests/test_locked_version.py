from pathlib import Path
import subprocess
import sys
import tempfile
import textwrap
import unittest


class LockedVersionTests(unittest.TestCase):
    def run_version_reader(self, requirements):
        action = Path(__file__).resolve().parents[1] / "action.yml"
        code = action.read_text(encoding="utf-8").split("<<'PY'\n", 1)[1].split("\n        PY\n", 1)[0]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "requirements.txt"
            path.write_text(requirements, encoding="utf-8")
            return subprocess.run(
                [sys.executable, "-", str(path), "poetry"],
                input=textwrap.dedent(code),
                capture_output=True,
                text=True,
            )

    def test_same_version_across_marked_entries_is_unambiguous(self):
        result = self.run_version_reader(
            'poetry-plugin==9.0\n'
            'poetry==2.5.1 ; sys_platform == "win32"\n'
            'poetry==2.5.1 ; sys_platform != "win32"\n'
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "2.5.1")

    def test_different_locked_versions_fail_instead_of_selecting_the_first(self):
        result = self.run_version_reader(
            'poetry==2.5.1 ; python_version < "3.12"\n'
            'poetry==2.5.2 ; python_version >= "3.12"\n'
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Expected one locked version", result.stderr)


if __name__ == "__main__":
    unittest.main()
