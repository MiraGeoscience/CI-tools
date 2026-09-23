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

To trigger it from any public or private repository, create a local workflow with an
`issue_comment` trigger and a job-level `if` that matches `/bot-approve` for trusted associations
(`COLLABORATOR` / `MEMBER` / `OWNER`), or use `workflow_dispatch` with an explicit PR number, then
call this reusable workflow and pass:

- `secrets.org-shared-app-id`: GitHub App ID
- `secrets.org-shared-app-key`: GitHub App private key

The reusable workflow handles all command logic for `/bot-approve`: it validates authorization,
replies to unauthorized users, acknowledges authorized users with a thumbs-up, checks prior human
approval, and can optionally enable auto-merge (merge commits only).

Authorization is granted only when:
- comment-triggered requests are valid PR comments containing `/bot-approve`, and either the
  requester has repository role `admin`/`maintain` or is an organization `MEMBER`/`OWNER` on a
  same-organization PR (head owner == base owner), including org-owned forks
- manually dispatched requests are initiated by a requester with repository role `admin`/`maintain`

GitHub App permissions required for the bot identity:
- Pull requests: Read and write
- Contents: Read and write
- Issues: Read and write

Enforce caller-side authorization in the calling workflow (`if` + trusted associations and/or
manual dispatch restrictions) because organization Actions policies are not scoped per workflow.

Security model note:
- authorization is enforced in the reusable workflow itself, so weakening caller-side conditions in
  another repository does not bypass role/association checks in this workflow
- `issue_comment` runs from the target repository default branch workflow definition (not PR code)
- if an attacker can push workflow changes to the protected/default branch in the caller repository,
  they can change any CI policy; protect that branch and workflow files with branch protections,
  CODEOWNERS review, and restricted write/admin membership
