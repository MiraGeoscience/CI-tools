"""Detect concrete test changes in a pull request.

A file counts if not removed, its path matches TEST_FILE_PATTERN (case-insensitive), and it adds a
non-blank, non-comment line (or has additions but no patch: binary or large diff).
Outputs 'has-tests' (true/false) and 'test-files' (newline-separated).
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import uuid
from pathlib import Path
from urllib.request import Request, urlopen

DEFAULT_PATTERN = r"(^|/)tests?/|(^|/)test_[^/]*\.py$|_test\.py$"
# '# ...' (not '#include'), '//', '/* */' block lines, docstring quotes
COMMENT = re.compile(r"""^(#(\s|$)|//|/\*|\*/|\*(\s|$)|\"\"\"|''')""")
PER_PAGE = 100


def fetch_files(api_url: str, repository: str, pr_number: str, token: str) -> list[dict]:
    """All PR files, paginated (GitHub caps at 3000)."""
    files: list[dict] = []
    page = 1
    while True:
        request = Request(
            f"{api_url}/repos/{repository}/pulls/{pr_number}/files?per_page={PER_PAGE}&page={page}",
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {token}",
                "X-GitHub-Api-Version": "2022-11-28",
            },
        )
        with urlopen(request, timeout=30) as response:  # noqa: S310 (fixed https API URL)
            batch = json.load(response)
        files.extend(batch)
        if len(batch) < PER_PAGE:
            return files
        page += 1


def is_concrete(patch: str | None, additions: int) -> bool:
    """True if an added line is neither blank nor a comment."""
    if patch is None:
        return additions > 0
    for line in patch.splitlines():
        if not line.startswith("+"):
            continue
        text = line[1:].strip()
        if text and not COMMENT.match(text):
            return True
    return False


def test_files(files: list[dict], pattern: re.Pattern[str]) -> list[str]:
    """Test files with concrete changes."""
    return [
        file["filename"]
        for file in files
        if file.get("status") != "removed"
        and pattern.search(file["filename"])
        and is_concrete(file.get("patch"), file.get("additions", 0))
    ]


def write_output(name: str, value: str) -> None:
    output = os.environ.get("GITHUB_OUTPUT")
    if not output:
        return
    delimiter = f"EOF_{uuid.uuid4().hex}"
    with open(output, "a", encoding="utf-8") as handle:
        handle.write(f"{name}<<{delimiter}\n{value}\n{delimiter}\n")


def write_summary(found: list[str]) -> None:
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if not summary:
        return
    with open(summary, "a", encoding="utf-8") as handle:
        if found:
            handle.write("### Concrete test changes\n\n" + "".join(f"- `{name}`\n" for name in found) + "\n")
        else:
            handle.write("### Concrete test changes\n\nNo concrete test changes found.\n\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--files-json", type=Path, help="read a saved 'pulls/<n>/files' response (local testing)")
    args = parser.parse_args()

    env = os.environ
    pattern = re.compile(env.get("TEST_FILE_PATTERN") or DEFAULT_PATTERN, re.IGNORECASE)
    if args.files_json:
        files = json.loads(args.files_json.read_text(encoding="utf-8"))
    else:
        files = fetch_files(
            env.get("GITHUB_API_URL", "https://api.github.com"),
            env["GITHUB_REPOSITORY"],
            env["PR_NUMBER"],
            env["GITHUB_TOKEN"],
        )

    found = test_files(files, pattern)
    print(f"{len(files)} changed file(s) in the pull request")
    if found:
        print("Concrete test changes:")
        for name in found:
            print(f"  {name}")
    else:
        print("No concrete test changes found")

    write_output("has-tests", "true" if found else "false")
    write_output("test-files", "\n".join(found))
    write_summary(found)
    return 0


if __name__ == "__main__":
    sys.exit(main())
