"""Job summary and PR comment: change counts and explicit dependency changes (with git commits, which
pixi-diff-to-markdown shows as 'unknown'), then all changes in the summary only."""
from __future__ import annotations

import json
import os
import re
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

COMMENT_MAX_CHARS = 60000  # GitHub limit: 65536
PRIORITY = ["downgraded", "major", "minor", "patch", "updated", "rebuilt", "added", "removed"]
LABELS = {"downgraded": "⚠️ Downgrade", "major": "Major upgrade", "minor": "Minor upgrade", "patch": "Patch upgrade",
          "updated": "Update", "rebuilt": "New commit", "added": "Added", "removed": "Removed"}

env = os.environ
temp = Path(env["RUNNER_TEMP"])
diff = json.loads((temp / "diff.json").read_text(encoding="utf-8"))

def git_ref(package: dict) -> tuple[str, str, str] | None:
    """Repo, ref and commit of 'git+<repo>[?rev=|branch=|tag=<ref>][&subdirectory=...]#<sha>'."""
    url = package.get("pypi", "")
    parts = urlsplit(url.removeprefix("git+"))
    if not url.startswith("git+") or not re.fullmatch(r"[0-9a-f]{7,40}", parts.fragment):
        return None
    query = parse_qs(parts.query)
    rev = next((query[key][0] for key in ("rev", "branch", "tag") if key in query), "")
    return f"{parts.scheme}://{parts.netloc}{parts.path}".removesuffix(".git"), rev, parts.fragment

def version(package: dict) -> str:
    """Conda: from the file name '<name>-<version>-<build>.conda'. PyPI: version field."""
    if "conda" in package:
        parts = package["conda"].rsplit("/", 1)[-1].removesuffix(".conda").removesuffix(".tar.bz2").rsplit("-", 2)
        if len(parts) == 3:
            return parts[1]
    return package.get("version", "")

def release(text: str) -> tuple[int, ...] | None:
    """Numeric release without epoch, padded for comparison: '1!2.10rc1' -> (2, 10, 0, ...)."""
    match = re.match(r"\d+(?:\.\d+)*", text.split("!")[-1])
    return tuple(map(int, match.group().split("."))) + (0,) * 8 if match else None

def classify(before: dict | None, after: dict | None) -> str:
    if before is None or after is None:
        return "added" if before is None else "removed"
    if version(before) == version(after):
        return "rebuilt"
    old, new = release(version(before)), release(version(after))
    if old is None or new is None or old == new:
        return "updated"  # e.g. pre-release change
    if new < old:
        return "downgraded"
    return "major" if new[0] != old[0] else "minor" if new[1] != old[1] else "patch"

def cell(package: dict | None) -> str:
    if package is None:
        return ""
    if ref := git_ref(package):
        repo, rev, sha = ref
        return f"{f'`{rev}` @ ' if rev else ''}[`{sha[:8]}`]({repo}/commit/{sha}) ({package.get('version', '')})"
    return version(package)

# one status per package name (the most significant across environments and platforms),
# one row per distinct explicit change (environments may resolve different versions)
status, rows = {}, {}
for platforms in diff["environment"].values():
    for packages in platforms.values():
        for package in packages:
            name, before, after = package["name"], package.get("before"), package.get("after")
            change = classify(before, after)
            if name not in status or PRIORITY.index(change) < PRIORITY.index(status[name]):
                status[name] = change
            if package.get("explicit") and cell(before) != cell(after):
                label = LABELS[change]
                old_ref, new_ref = before and git_ref(before), after and git_ref(after)
                if old_ref and new_ref and old_ref[0] == new_ref[0] and "github.com" in new_ref[0]:
                    label += f" ([compare]({new_ref[0]}/compare/{old_ref[2]}...{new_ref[2]}))"
                rows.setdefault((name, cell(before), cell(after)), label)

counts = {change: list(status.values()).count(change) for change in PRIORITY}
parts = [
    (counts["major"] + counts["minor"] + counts["patch"], "upgraded" + (f" ({counts['major']} major)" if counts["major"] else "")),
    (counts["downgraded"], "⚠️ downgraded"),
    (counts["updated"], "other version changes"),
    (counts["rebuilt"], "rebuilt (same version)"),
    (counts["added"], "added"),
    (counts["removed"], "removed"),
]
stats = f"**{len(status)}** package{'s' if len(status) > 1 else ''} changed: {', '.join(f'{n} {label}' for n, label in parts if n)}." if status else "*No package changes.*"

table = []
if rows:
    lines = ["|Dependency|Before|After|Change|", "|-|-|-|-|"] + [f"|{n}|{b}|{a}|{c}|" for (n, b, a), c in sorted(rows.items())]
    # collapse long tables
    table = ["### Explicit dependencies", "", *lines, ""] if len(rows) <= 15 else [
        "<details>", f"<summary><b>Explicit dependencies</b> ({len(rows)} changes)</summary>", "", *lines, "", "</details>", ""]

head = [
    env["COMMENT_MARKER"],
    f"## 📦 Changes in `{env['LOCKFILE_PATH']}`",
    "",
    f"Comparing [`{env['BASE_SHA'][:8]}`]({env['REPO_URL']}/commit/{env['BASE_SHA']}) to "
    f"[`{env['HEAD_SHA'][:8]}`]({env['REPO_URL']}/commit/{env['HEAD_SHA']}) ([workflow run]({env['RUN_URL']})).",
    "",
    stats,
    "",
]
everything = (temp / "dependencies.md").read_text(encoding="utf-8")
summary = head + table + (["### All changes", "", everything] if everything.strip() != "No diff" else [])
with open(env["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as file:
    file.write("\n".join(summary) + "\n")

link = f"📋 **[Full report in the job summary]({env['RUN_URL']}{'#summary-' + env['JOB_ID'] if env.get('JOB_ID') else ''})**"
comment = "\n".join(head + table + [link])
if len(comment) > COMMENT_MAX_CHARS:
    print(f"::notice::PR comment too large ({len(comment)} characters): leaving out the explicit dependencies")
    comment = "\n".join(head + ["> [!NOTE]", "> The explicit dependency changes are too large for a comment.", "", link])
(temp / "comment.md").write_text(comment + "\n", encoding="utf-8")
print(comment)
