# CI-tools

## Overview

CI-tools is a repository designed to streamline and standardize Continuous Integration (CI) processes across MiraGeoscience's projects. It encapsulates reusable GitHub Actions workflows for common CI tasks, promoting efficiency and consistency.

## Structure

```
|__ .github/workflows: Containing CI-tools workflows
|__ github-workflows: Containing reusable workflows for different project types and tasks. 
    |__ python: workflows tailored for Python projects, including static analysis and testing.
    |__ jira: workflow for creating JIRA issues.
```

## Usage

- Create a new GitHub Actions workflow in your project's `.github/workflows` directory.
- Include the desireded reusable workflow using the `uses` keyword:
```yaml
jobs:
  call-workflow-create-jira-issue:
    uses: MiraGeoscience/CI-tools/<path_to_the_reusable_workflows> 
    # e.g.: uses: MiraGeoscience/CI-tools/github-workflows/jira/issue_to_jira.yml
```
