from pathlib import Path
import subprocess
import sys
import textwrap


def run_version_reader(tmp_path, requirements):
    action = Path(__file__).resolve().parents[1] / "action.yml"
    code = action.read_text(encoding="utf-8").split("<<'PY'\n", 1)[1].split("\n        PY\n", 1)[0]
    path = tmp_path / "requirements.txt"
    path.write_text(requirements, encoding="utf-8")
    return subprocess.run(
        [sys.executable, "-", str(path), "poetry"],
        input=textwrap.dedent(code),
        capture_output=True,
        text=True,
    )


def test_same_version_across_marked_entries_is_unambiguous(tmp_path):
    result = run_version_reader(
        tmp_path,
        'poetry-plugin==9.0\n'
        'poetry==2.5.1 ; sys_platform == "win32"\n'
        'poetry==2.5.1 ; sys_platform != "win32"\n'
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "2.5.1"


def test_different_locked_versions_fail_instead_of_selecting_the_first(tmp_path):
    result = run_version_reader(
        tmp_path,
        'poetry==2.5.1 ; python_version < "3.12"\n'
        'poetry==2.5.2 ; python_version >= "3.12"\n'
    )
    assert result.returncode != 0
    assert "Expected one locked version" in result.stderr
