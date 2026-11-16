"""Submit configured native tool versions without claiming transitive coverage."""

import argparse
import datetime
import json
import os
from pathlib import Path
import re
import tomllib
import urllib.request


CATALOG = ".github/actions/setup-ci-tool/native_tools.toml"


def load_tools(root):
    path = root / CATALOG
    if not path.resolve().is_relative_to(root.resolve()):
        raise ValueError("Native tool catalog must stay within the source checkout")
    with path.open("rb") as stream:
        catalog = tomllib.load(stream)
    tools = catalog.get("tools", [])
    if catalog.get("schema") != 1 or not tools:
        raise ValueError("Expected a nonempty native tool catalog with schema 1")
    packages = set()
    for tool in tools:
        package = tool["package"]
        if not re.fullmatch(r"pkg:(?:github|conda)/[\w.-]+(?:/[\w.-]+)?", package) or package in packages:
            raise ValueError("Native tool package identities must be valid and unique")
        packages.add(package)
        if not re.fullmatch(r"[A-Za-z0-9_. -]{1,80}", tool["name"]):
            raise ValueError("Invalid native tool name")
        for field in ["advisories", "releases", "installer"]:
            if field in tool:
                repository = tool[field]
                if not re.fullmatch(r"[\w.-]+/[\w.-]+", repository) or any(
                    part in {".", ".."} for part in repository.split("/")
                ):
                    raise ValueError("Invalid native tool repository")
        if "advisories" not in tool:
            raise ValueError("Missing native tool advisory repository")
        source = tool["source"]
        if not source.startswith(".github/") or "\\" in source or ".." in source.split("/"):
            raise ValueError("Native tool sources must stay within .github")
        if re.compile(tool["pattern"]).groups != 1:
            raise ValueError("Native version patterns require exactly one capture group")
    return tools


def version(pattern, text):
    matches = set(re.findall(pattern, text, re.MULTILINE))
    if len(matches) != 1:
        raise ValueError(f"Expected one fixed tool version, found {sorted(matches)}")
    return matches.pop()


def installer_version(installer, ref, pattern):
    url = f"https://raw.githubusercontent.com/{installer}/{ref}/action.yml"
    with urllib.request.urlopen(url, timeout=30) as response:
        action = response.read().decode("utf-8")
    return version(pattern, action)


def tool_versions(root, tools=None):
    purls = set()
    for tool in load_tools(root) if tools is None else tools:
        paths = sorted(root.glob(tool["source"]))
        if not paths:
            raise ValueError(f"Missing native tool source: {tool['source']}")
        text = []
        for path in paths:
            if not path.resolve().is_relative_to(root.resolve()):
                raise ValueError("Native tool source must stay within the source checkout")
            text.append(path.read_text(encoding="utf-8"))
        text = "\n".join(text)
        if "installer" in tool:
            installer = tool["installer"]
            refs = set(re.findall(re.escape(installer) + r"@([a-f0-9]{40})\b", text))
            if not refs:
                raise ValueError(f"No SHA-pinned installers found for {tool['name']}")
            versions = {installer_version(installer, ref, tool["pattern"]) for ref in sorted(refs)}
        else:
            versions = {version(tool["pattern"], text)}
        suffix = "?" + tool["qualifiers"] if tool.get("qualifiers") else ""
        for pinned in versions:
            purls.add(f"{tool['package']}@{tool.get('version_prefix', '')}{pinned}{suffix}")
    return purls


def build_snapshot(purls, environment):
    if not purls:
        raise ValueError("Empty native tool inventory")
    return {
        "version": 0,
        "sha": environment["GITHUB_SHA"],
        "ref": environment["GITHUB_REF"],
        "job": {
            "id": environment["GITHUB_RUN_ID"],
            "correlator": "ci-tools-direct-versions",
            "html_url": (
                f"{environment['GITHUB_SERVER_URL']}/{environment['GITHUB_REPOSITORY']}"
                f"/actions/runs/{environment['GITHUB_RUN_ID']}"
            ),
        },
        "detector": {
            "name": "ci-tools-direct-inventory",
            "version": "1.0.0",
            "url": "https://github.com/MiraGeoscience/CI-tools",
        },
        "scanned": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "manifests": {
            "ci-native-tool-versions": {
                "name": "ci-native-tool-versions",
                "metadata": {"evidence": "configured-tool-versions", "transitive-coverage": False},
                "resolved": {
                    purl: {"package_url": purl, "relationship": "direct", "scope": "development"}
                    for purl in sorted(purls)
                },
            }
        },
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    purls = tool_versions(Path.cwd())
    snapshot = build_snapshot(purls, os.environ)
    args.output.write_text(json.dumps(snapshot, indent=2) + "\n", encoding="utf-8")
    print(f"Prepared {len(purls)} configured tool versions (no transitive coverage)")


if __name__ == "__main__":
    main()
