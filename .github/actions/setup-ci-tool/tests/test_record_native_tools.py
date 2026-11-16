import importlib.util
import json
from pathlib import Path
import subprocess
import sys

import pytest


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
SPEC = importlib.util.spec_from_file_location(
    "record_native_tools", Path(__file__).resolve().parents[1] / "record_native_tools.py",
)
recorder = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(recorder)
TOOLS = recorder.load_tools(Path(__file__).resolve().parents[4])


def test_resolves_floating_pixi_and_jfrog_from_installed_cli(monkeypatch):
    calls = []

    def version(command, **kwargs):
        calls.append(command)
        return subprocess.CompletedProcess(command, 0, stdout=f"{command[0]} version 9.8.7\n")

    monkeypatch.setattr(recorder.subprocess, "run", version)
    purls, errors = recorder.collect({"Pixi": "", "JFrog CLI": ""}, TOOLS)
    assert not errors
    assert calls == [["pixi", "--version"], ["jf", "--version"]]
    assert purls == [
        "pkg:github/jfrog/jfrog-cli@v9.8.7",
        "pkg:github/prefix-dev/pixi@v9.8.7",
    ]


def test_preserves_micromamba_release_build_and_conda_qualifiers():
    purls, errors = recorder.collect({"micromamba": "2.1.0-0", "pixi-diff": "1.2.3"}, TOOLS)
    assert not errors
    assert purls == [
        "pkg:conda/pixi-diff@1.2.3?channel=conda-forge",
        "pkg:github/mamba-org/micromamba-releases@2.1.0-0",
    ]


@pytest.mark.parametrize("requested", [{"Pixi": "latest"}, {"Pixi": "1.2.3;echo secret"}, {"unknown": "1.2.3"}])
def test_invalid_requests_do_not_publish_versions_or_leak_input(requested):
    assert recorder.collect(requested, TOOLS) == ([], ["tool-version-collection-failed"])


def test_ambiguous_cli_version_withholds_publication(monkeypatch):
    monkeypatch.setattr(
        recorder.subprocess, "run",
        lambda *args, **kwargs: subprocess.CompletedProcess(args, 0, stdout="1.2.3 and 4.5.6"),
    )
    assert recorder.collect({"Pixi": ""}, TOOLS)[1] == ["tool-version-collection-failed"]


@pytest.mark.parametrize("event_name,ref,expected", [
    ("push", "refs/heads/trunk", True),
    ("workflow_dispatch", "refs/heads/trunk", True),
    ("schedule", "refs/heads/trunk", True),
    ("pull_request_target", "refs/heads/trunk", False),
    ("pull_request", "refs/pull/1/merge", False),
    ("push", "refs/tags/trunk", False),
    ("push", "refs/heads/main", False),
])
def test_only_trusted_default_branch_events_emit_artifacts(event_name, ref, expected):
    environment = {"GITHUB_EVENT_NAME": event_name, "GITHUB_REF": ref}
    assert recorder.eligible(environment, {"repository": {"default_branch": "trunk"}}) is expected


@pytest.mark.parametrize("requested,expected_errors", [
    ('{"Pixi": "v9.8.7"}', []),
    ("invalid JSON", ["invalid-tool-request"]),
])
def test_main_records_run_provenance_and_upload_path(tmp_path, monkeypatch, requested, expected_errors):
    event = tmp_path / "event.json"
    event.write_text('{"repository": {"default_branch": "trunk"}}', encoding="utf-8")
    output = tmp_path / "outputs"
    environment = {
        "GITHUB_EVENT_NAME": "push", "GITHUB_REF": "refs/heads/trunk",
        "GITHUB_REPOSITORY": "example/caller", "GITHUB_SHA": "a" * 40,
        "GITHUB_RUN_ID": "42", "GITHUB_RUN_ATTEMPT": "2",
        "GITHUB_EVENT_PATH": str(event), "GITHUB_OUTPUT": str(output), "RUNNER_TEMP": str(tmp_path),
    }
    for key, value in environment.items():
        monkeypatch.setenv(key, value)
    monkeypatch.setattr(sys, "argv", ["record_native_tools.py", "--tools", requested])
    recorder.main()
    values = dict(line.split("=", 1) for line in output.read_text(encoding="utf-8").splitlines())
    record = json.loads(Path(values["path"]).read_text(encoding="utf-8"))
    assert values["name"].startswith("ci-tools-native-2-")
    assert record["repository"] == "example/caller"
    assert record["sha"] == environment["GITHUB_SHA"]
    assert record["ref"] == environment["GITHUB_REF"]
    assert (record["run_id"], record["run_attempt"]) == (42, 2)
    assert record["errors"] == expected_errors
    assert record["tools"] == ([] if expected_errors else ["pkg:github/prefix-dev/pixi@v9.8.7"])
