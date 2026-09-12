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

To trigger it from any public or private repository, create a local workflow in that repository with
an `issue_comment` trigger, then call this reusable workflow when an authorized user comments `/bot-approve`:

- `with.pr-number`: PR number to approve
- `secrets.org-shared-app-id`: GitHub App ID
- `secrets.org-shared-app-key`: GitHub App private key

For comment-triggered use, gate authorized users in the caller workflow (for example by checking
`github.event.comment.author_association`), reply to unauthorized users when they invoke `/bot-approve`,
and apply organization Actions policies to restrict who can run it.
