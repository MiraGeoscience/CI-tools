# CI-tools

## Overview

CI-tools centralizes reusable GitHub Actions workflows and composite actions
for MiraGeoscience projects.

## Structure

```
.github/
  actions/        Composite actions and shared CI tooling
  workflows/      Reusable workflows and repository checks
  instructions/   Scoped guidance for coding agents and reviewers
AGENTS.md         Agent onboarding, instruction index, and validation commands
```

## Usage

Create a workflow in your project's `.github/workflows` directory and call a
reusable workflow with `uses`:

```yaml
jobs:
  call-workflow-create-jira-issue:
    uses: MiraGeoscience/CI-tools/<path_to_the_reusable_workflows>@<full_commit_sha>
    # e.g.: uses: MiraGeoscience/CI-tools/.github/workflows/reusable-jira-issue_to_jira.yml@<full_commit_sha>
```

Pin `uses:` to a full commit SHA of CI-tools in calling repositories (Dependabot keeps it up to
date).

## Referencing CI-tools from within CI-tools

Reusable workflows and actions of this repository reference each other with the self-repository
syntax, for example: `uses: $/.github/actions/setup-zizmor-config`.

`$/` resolves to CI-tools at the
exact commit that is running, so a caller pinned to a commit SHA runs every nested workflow and
action from that same commit, and internal references never need a SHA or tag update.
Do not use `MiraGeoscience/CI-tools/...@<ref>` for internal references.

## CI tool dependencies

### Coverage and update policy

| Dependencies | Dependabot advisory alerts | Automatic version-update PRs | Tracking |
|--------------|----------------------------|------------------------------|----------|
| PyPI tools in the shared uv manifest and lock | Supported for direct and transitive packages | Yes, within manifest constraints | Dependabot `uv` |
| Third-party GitHub Actions | Supported for the action itself, not everything it installs | Yes, updates to action pins | Dependabot `github-actions` |
| Other native tools listed below | No general Dependabot CVE coverage, direct or transitive | No independent tool-version updates | Native inventory and private upstream advisory monitor |

Alerts require a matching GitHub-reviewed advisory and enabled Dependabot
alerts; being in the dependency graph alone is not sufficient.

Configured Dependabot version updates run weekly with a four-day cooldown.
Automatic security-update PRs are a separate, optional setting; alerts can be
triaged privately and fixes opened manually. Urgent security fixes should not wait for the routine
cooldown. Calling repositories must update their pinned CI-tools commit to
receive a fix.

Runner-provided tools and caller-owned project, build-backend, and hook
dependencies are outside this repository's tooling coverage.

### Python tooling

CI-owned PyPI tools use patch-compatible constraints in
`.github/actions/setup-ci-tool/tooling/pyproject.toml` and exact versions in
`uv.lock`. For example, `poetry~=2.5.1` permits patches below `2.6`, but
installation always uses the exact lock. uv itself is declared in this
manifest; `setup-uv` reads its exact version from the same lockfile.

The shared `setup-ci-tool` action exports and installs only the requested
dependency group. CLI tools run in isolated environments using Python 3.15 from
`actions/setup-python`, preserving the caller's Python and reusing GitHub's
runner tool cache when available. Library mode returns an explicit interpreter
path without activating the environment or adding it to PATH. Version-only
mode resolves the locked version without installing the requested tool.
The setup-uv dependency cache is keyed on the shared lockfile.

GitHub's built-in [Dependabot graph jobs](https://docs.github.com/en/code-security/concepts/supply-chain-security/dependency-graph-data#dependabot-graph-jobs)
provide uv transitive dependency coverage when the dependency graph is enabled;
no custom submission workflow or automatic-submission opt-in is needed.

To update the lock locally, run
`uv lock --project .github/actions/setup-ci-tool/tooling --upgrade`

The Zizmor and Codecov actions remain responsible for their binary installation
and verification, but receive versions derived from the matching PyPI packages.
The lockfile does not control dependencies bundled inside those native binaries.

### Native tool inventory

**Pixi, micromamba, rattler-build, `pixi-diff`, `pixi-diff-to-markdown`, and
JFrog CLI** are outside the shared uv lock. The
[Submit native tool version inventory](.github/workflows/native-tool-inventory.yml)
workflow lists and submits their configured versions on relevant default-branch
pushes, weekly, and on manual dispatch. It reads existing production pins and
the fixed JFrog CLI defaults from SHA-pinned installers, without installing
tools, scanning binaries, or resolving transitive dependencies. Its logical
inventory does not override native action or uv dependency graphs.

Inventory submission and DevOps monitoring share
[one native tool catalog](.github/actions/setup-ci-tool/native_tools.toml).
It declares identities and pin sources, not duplicate version pins.

The GitHub release and Conda identities provide **version visibility only**,
not general CVE coverage for these tools or their bundled dependencies.
GitHub Actions advisory support applies to actions, not arbitrary binaries
hosted on GitHub. JFrog CLI's default can advance when its setup action is
updated; this is not independent CLI version tracking.

See [GitHub's dependency submission requirements](https://docs.github.com/en/rest/dependency-graph/dependency-submission#about-dependency-submissions).

### Caller native inventories

On default-branch pushes, schedules, and manual runs, native installers record
the effective versions as small workflow artifacts. Floating Pixi versions and
JFrog CLI defaults are resolved from the installed CLI; fixed micromamba release
pins retain their build suffix. Caller Python and token permissions are unchanged.

A separate publisher in the **private DevOps repository**, once configured,
imports completed runs into each participating caller's dependency graph as
direct development dependencies. Matrix jobs are combined per caller workflow,
without overriding other workflows, action dependencies, or uv manifests.
PRs and tags are excluded; the PR-only Pixi diff workflow does not contribute
default-branch inventory. Collection failures do not fail caller builds.

Callers only need the normal CI-tools commit-pin update, not extra workflow
steps, secrets, or permission declarations. The private DevOps repository
documents the dedicated GitHub App, repository allowlist, and operational limits.

### Private native advisory monitoring

A daily monitor in the **private DevOps repository** reports published upstream
advisories and new stable releases with security-keyword matches as private
issues. Applicability and fixes require human triage; this is not Dependabot
alerting or a binary audit.

The private DevOps repository documents setup, notifications, privacy, and
coverage limitations.
