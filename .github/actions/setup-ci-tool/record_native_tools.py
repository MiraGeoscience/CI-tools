"""Record effective caller tool versions without granting caller jobs write access."""

import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import uuid

from tool_inventory import load_tools


VERSION = re.compile(r"v?\d+\.\d+\.\d+(?:-[\w.-]+)?")
EVENTS = {"push", "schedule", "workflow_dispatch"}


def eligible(environment, event):
    return (
        environment["GITHUB_EVENT_NAME"] in EVENTS
        and environment["GITHUB_REF"] == f"refs/heads/{event['repository']['default_branch']}"
    )


def collect(requested, tools):
    if not isinstance(requested, dict) or len(requested) > len(tools):
        raise ValueError("Expected a native tool name/version mapping")
    catalog = {tool["name"]: tool for tool in tools}
    purls, errors = set(), []
    for name, pinned in requested.items():
        try:
            tool = catalog[name]
            if not isinstance(pinned, str):
                raise ValueError("Invalid tool version")
            if not pinned:
                command = tool["version_command"]
                if not re.fullmatch(r"[\w-]+", command):
                    raise ValueError("Invalid version command")
                result = subprocess.run(
                    [command, "--version"], capture_output=True, text=True, check=True, timeout=30,
                )
                matches = set(re.findall(r"\b\d+\.\d+\.\d+(?:-[\w.-]+)?", result.stdout))
                if len(matches) != 1:
                    raise ValueError("Ambiguous installed version")
                pinned = matches.pop()
            if not VERSION.fullmatch(pinned) or len(pinned) > 80:
                raise ValueError("Expected a fixed version")
            prefix = tool.get("runtime_prefix", tool.get("version_prefix", ""))
            suffix = "?" + tool["qualifiers"] if tool.get("qualifiers") else ""
            purls.add(f"{tool['package']}@{prefix}{pinned.removeprefix('v')}{suffix}")
        except (KeyError, ValueError, OSError, subprocess.SubprocessError):
            errors.append("tool-version-collection-failed")
    return sorted(purls), errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tools", required=True)
    args = parser.parse_args()
    with Path(os.environ["GITHUB_EVENT_PATH"]).open(encoding="utf-8") as stream:
        event = json.load(stream)
    if not eligible(os.environ, event):
        return
    tools = load_tools(Path(__file__).resolve().parents[3])
    try:
        purls, errors = collect(json.loads(args.tools), tools)
    except ValueError:
        purls, errors = [], ["invalid-tool-request"]
    record = {
        "schema": 1,
        "repository": os.environ["GITHUB_REPOSITORY"],
        "sha": os.environ["GITHUB_SHA"],
        "ref": os.environ["GITHUB_REF"],
        "run_id": int(os.environ["GITHUB_RUN_ID"]),
        "run_attempt": int(os.environ["GITHUB_RUN_ATTEMPT"]),
        "tools": purls,
        "errors": errors,
    }
    name = f"ci-tools-native-{record['run_attempt']}-" + uuid.uuid4().hex
    directory = Path(os.environ["RUNNER_TEMP"]) / name
    directory.mkdir()
    output = directory / "inventory.json"
    output.write_text(json.dumps(record) + "\n", encoding="utf-8")
    with Path(os.environ["GITHUB_OUTPUT"]).open("a", encoding="utf-8") as stream:
        stream.write(f"name={name}\npath={output}\n")
    if errors:
        print("::warning::Native tool versions could not be fully collected; graph publication will be withheld.")


if __name__ == "__main__":
    main()
