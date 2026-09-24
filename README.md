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
    uses: MiraGeoscience/CI-tools/<path_to_the_reusable_workflows>
    # e.g.: uses: MiraGeoscience/CI-tools/.github/workflows/reusable-jira-issue_to_jira.yml
```

Pin `uses:` to a full commit SHA of CI-tools (Dependabot keeps it up to date), and grant the
calling job only the permissions listed by the reusable workflow; reusable workflows here declare
`permissions: {}` at the top and request per-job permissions.

## Zizmor analysis

`reusable-zizmor-security.yml` is the single entry point for zizmor scans
(`reusable-zizmor-annotate.yml` and `reusable-zizmor-advanced-security.yml` are deprecated). Call it
from one job; the expression job name keeps the check contexts required by the organization
rulesets (`Zizmor analysis (annotate) / Security Scan` on pull requests):

```yaml
permissions: {}
jobs:
  call-workflow-zizmor:
    name: ${{ github.event_name == 'pull_request' && 'Zizmor analysis (annotate)' || 'Zizmor analysis (advanced security)' }}
    permissions:
      contents: read
      actions: read
      security-events: write  # public repositories only (advanced-security)
    uses: MiraGeoscience/CI-tools/.github/workflows/reusable-zizmor-security.yml@<sha>
    with:
      annotations: ${{ github.event_name == 'pull_request' }}
      advanced-security: ${{ github.event_name != 'pull_request' }}  # use false for private repositories
```

The reusable workflow inherits the caller job permissions: `contents: read` and `actions: read`,
plus `security-events: write` when `advanced-security` is true (requires a public repository or
GitHub Advanced Security).
