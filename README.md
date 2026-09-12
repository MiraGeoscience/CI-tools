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

## Bot PR approval workflow

This repository provides a reusable workflow for bot-driven PR approval and optional auto-merge:
`MiraGeoscience/CI-tools/.github/workflows/reusable-bot-pr-approval.yml@<ref>`.

To trigger it from any public or private repository, create a local workflow with only an
`issue_comment` trigger that calls this reusable workflow and passes:

- `secrets.org-shared-app-id`: GitHub App ID
- `secrets.org-shared-app-key`: GitHub App private key

The reusable workflow handles all command logic for `/bot-approve`: it validates authorization,
replies to unauthorized users, acknowledges authorized users with a thumbs-up, checks prior human
approval, and enables auto-merge using a merge commit.

Apply organization Actions policies to restrict who can run it.
