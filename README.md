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

## Pixi testing and static analysis

Use the existing `reusable-python-pytest.yml` and
`reusable-python-static_analysis.yml` workflows with `package-manager: pixi`.
They check lock freshness and run tasks frozen in the explicitly selected
environment. `pixi-version` can pin Pixi independently of the action version.

The optional `pixi-setup-task` input runs a project task once during environment
setup, before tests or linting. For example, an `install` task can perform
`uv pip install --no-deps --editable .` followed by `uv pip check`. Leave it
unset when the workflow only needs the source checkout. Test and lint tasks
do not need to depend on installation.

```yaml
jobs:
  pytest:
    uses: MiraGeoscience/CI-tools/.github/workflows/reusable-python-pytest.yml@<full_commit_sha>
    with:
      package-manager: pixi
      pixi-version: v0.67.2
      python-versions: '["3.12", "3.13", "3.14"]'
      pixi-setup-task: install
      os: '["ubuntu-latest", "windows-latest"]'
```

The standard workflows run pytest and pylint directly. Set `pixi-task` only
when a project needs a nonstandard command or working directory.

`reusable-python-setup_pixi` also exposes the selected name as the
`environment-name` output and accepts the corresponding `setup-task` input
when used directly.

## Updating Poetry tooling

From the repository root, refresh Poetry, its dynamic-versioning plugin, and
their dependencies within the tooling manifest's version constraints:

```powershell
uv lock --project .github\actions\reusable-python-setup_poetry\tooling --upgrade
```

Review and commit the updated `uv.lock`. To change the allowed version range,
edit `pyproject.toml` in the same directory before running the command.
