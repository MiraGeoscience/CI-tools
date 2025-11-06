# GitHub CI Scripts

Helper scripts for GitHub CI workflows used by MiraGeoscience.

## Overview

This package provides utility functions and CLI commands for version checking and validation in CI/CD pipelines.

## Installation

This package is designed to be used with `uv` in GitHub Actions workflows:

```bash
uv run check-version --help
```

## Development

The package uses:

- `typer` for CLI interface
- `packaging` for version parsing and normalization
- `uv` for dependency management and execution
