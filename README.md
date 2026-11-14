# CI-tools

## Overview

CI-tools is a repository designed to streamline and standardize Continuous Integration (CI) processes across MiraGeoscience's projects. It encapsulates reusable GitHub Actions workflows for common CI tasks, promoting efficiency and consistency.

## Structure

```
|_ .github
|____ actions: Containing reusable actions for setup python env
|____ workflows: Containing reusable workflows for different project types and tasks.
```

## Usage

- Create a new GitHub Actions workflow in your project's `.github/workflows` directory.
- Include the desired reusable workflows using the `uses` keyword:
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
syntax, for example `uses: $/.github/actions/setup-zizmor-config`. `$/` resolves to CI-tools at the
exact commit that is running, so a caller pinned to a commit SHA runs every nested workflow and
action from that same commit, and internal references never need a SHA or tag update.
Do not use `MiraGeoscience/CI-tools/...@<ref>` for internal references.

## CI tool dependencies

CI-owned PyPI tools use patch-compatible constraints in
`.github/actions/setup-ci-tool/tooling/pyproject.toml` and exact versions in
`uv.lock`. Dependabot's `uv` ecosystem updates the project weekly with a four-day
cooldown for routine updates. `poetry~=2.5.1` allows patches below `2.6`;
installation always uses the exact lock, never the latest matching release.

The shared `setup-ci-tool` action uses uv directly to export and install only
the requested dependency group. CLI tools remain isolated from the caller's
Python; library environments are not activated or added to the caller's PATH.
Version-only mode exports a group's locked version without installing that tool.
The setup-uv cache is keyed on the shared lockfile.

GitHub supports uv version updates, security alerts and security updates.
Its built-in [Dependabot graph jobs](https://docs.github.com/en/code-security/concepts/supply-chain-security/dependency-graph-data#dependabot-graph-jobs)
provide transitive dependency coverage automatically when the dependency graph
is enabled. No custom submission workflow or automatic-submission opt-in is
needed, and graph jobs do not consume billable Actions minutes.

To update the lock locally, run
`uv lock --project .github\actions\setup-ci-tool\tooling --upgrade`
(use `/` separators on Linux/macOS).

The Zizmor and Codecov actions remain responsible for their binary installation
and verification, but receive versions derived from the matching PyPI packages.
The lockfile does not control dependencies bundled inside those native binaries.
Dependabot alerts must also be enabled in repository settings. Automatic
security-update PRs are optional; alerts can be triaged privately and fixes
opened manually. Urgent security fixes should not wait for the routine cooldown;
calling repositories must also update their pinned CI-tools commit to receive
the fix.

Native tools without a matching supported package manifest remain exceptions:
Pixi, micromamba, rattler-build, `pixi-diff`, and `pixi-diff-to-markdown`.
Their existing version inputs are not independently updated by the PyPI
Dependabot entry. JFrog CLI currently uses the fixed defaults from its pinned
setup actions. Runner-provided tools and caller-owned project, build-backend,
and hook dependencies are outside the shared tooling lock.
