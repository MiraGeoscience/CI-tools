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

## Bot PR approval relay

`reusable-bot-pr-approval.yml` forwards `/bot-approve` pull request comments to the organization's
private controller, which performs all authorization and review-history checks before approving.
The relay contains no approval logic and no approval credentials.

Add this workflow to any repository (public or private) of the organization, pinned to a full
commit SHA of CI-tools:

```yaml
name: Bot PR approval
on:
  issue_comment:
    types: [created]
permissions: {}
jobs:
  call-workflow-bot-pr-approval:
    if: github.event.issue.pull_request && startsWith(github.event.comment.body, '/bot-approve')
    uses: MiraGeoscience/CI-tools/.github/workflows/reusable-bot-pr-approval.yml@<sha>
    secrets:
      relay-app-id: ${{ secrets.BOT_RELAY_APP_ID }}
      relay-app-private-key: ${{ secrets.BOT_RELAY_APP_PRIVATE_KEY }}
```

Then comment `/bot-approve` (alone on the first line) on a pull request. The controller reacts
with :eyes: and replies with the result.

`BOT_RELAY_APP_ID` / `BOT_RELAY_APP_PRIVATE_KEY` belong to the Relay GitHub App, which only has
*Actions: write* on the controller repository; they can be organization secrets. Do not add a
`workflow_dispatch` trigger to this caller: manual approvals are dispatched from the controller.
