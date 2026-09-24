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
