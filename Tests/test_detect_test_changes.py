"""Tests of .github/actions/detect-test-changes/detect_test_changes.py."""
from __future__ import annotations

import importlib.util
import json
import re
from pathlib import Path

import pytest

SCRIPT = Path(__file__).parents[1] / ".github/actions/detect-test-changes/detect_test_changes.py"
spec = importlib.util.spec_from_file_location("detect_test_changes", SCRIPT)
dtc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dtc)

PATTERN = re.compile(dtc.DEFAULT_PATTERN, re.IGNORECASE)


@pytest.mark.parametrize(
    "line",
    ["def test_a():", "    assert x == 1", '#include "foo.h"', "$this->assertTrue(true);", "*ptr = 1;"],
)
def test_code_line_is_concrete(line):
    assert dtc.is_concrete(f"@@ -0,0 +1 @@\n+{line}", 1)


@pytest.mark.parametrize(
    "line",
    ["", "   ", "# comment", "#", "// comment", "/* block", " * block", "*/", '"""Docstring."""', "'''"],
)
def test_comment_or_blank_line_is_not_concrete(line):
    assert not dtc.is_concrete(f"@@ -0,0 +1 @@\n+{line}", 1)


def test_removed_and_context_lines_are_ignored():
    assert not dtc.is_concrete("@@ -1,2 +1 @@\n-assert x\n assert y", 0)


def test_missing_patch_counts_additions():
    assert dtc.is_concrete(None, 3)
    assert not dtc.is_concrete(None, 0)


@pytest.mark.parametrize(
    ("path", "expected"),
    [
        ("tests/test_a.py", True),
        ("Tests/Base/ScriptTest.cpp", True),
        ("app/Library/Test/FooTest.php", True),
        ("src/test_utils.py", True),
        ("src/foo_test.py", True),
        ("src/contest.py", False),
        ("src/testing/helpers.py", False),
    ],
)
def test_default_pattern(path, expected):
    assert bool(PATTERN.search(path)) is expected


def test_test_files_filters_status_pattern_and_content():
    files = [
        {"filename": "src/app.py", "status": "modified", "additions": 1, "patch": "+x = 1"},
        {"filename": "tests/test_new.py", "status": "added", "additions": 1, "patch": "+def test_x(): pass"},
        {"filename": "tests/test_doc.py", "status": "modified", "additions": 1, "patch": "+# todo"},
        {"filename": "tests/test_old.py", "status": "removed", "additions": 0, "patch": "-def test_y(): pass"},
        {"filename": "tests/test_moved.py", "status": "renamed", "additions": 0},
    ]
    assert dtc.test_files(files, PATTERN) == ["tests/test_new.py"]


def test_main_writes_outputs(tmp_path, monkeypatch):
    files_json = tmp_path / "files.json"
    files_json.write_text(
        json.dumps([{"filename": "tests/test_a.py", "status": "added", "additions": 1, "patch": "+assert True"}]),
        encoding="utf-8",
    )
    output = tmp_path / "output"
    monkeypatch.setenv("GITHUB_OUTPUT", str(output))
    monkeypatch.delenv("GITHUB_STEP_SUMMARY", raising=False)
    monkeypatch.delenv("TEST_FILE_PATTERN", raising=False)
    monkeypatch.setattr("sys.argv", ["detect_test_changes.py", "--files-json", str(files_json)])

    assert dtc.main() == 0
    text = output.read_text(encoding="utf-8")
    assert re.search(r"has-tests<<(\S+)\ntrue\n\1\n", text)
    assert re.search(r"test-files<<(\S+)\ntests/test_a.py\n\1\n", text)
