# CI-tools agent guide

CI-tools provides reusable GitHub Actions workflows and composite actions for
MiraGeoscience projects. Workflow inputs, outputs, permissions, and caller
environment behavior are public interfaces: preserve them unless the requested
change explicitly requires otherwise.

## Repository map

- `.github/actions/`: composite actions and shared Python tooling.
- `.github/workflows/`: reusable workflows and this repository's checks.
- `.github/actions/setup-ci-tool/tooling/`: CI-owned PyPI manifest and uv lock.
- `.github/actions/setup-ci-tool/tests/`: pytest regression tests.
- `.github/dependabot.yml`: automatic updates for supported dependencies.
- `README.md`: usage, self-repository references, and dependency coverage limits.

## Working agreements

Keep changes focused and preserve unrelated work and staging. Do not commit,
push, or change repository security settings without a request.

Pin third-party actions to full commit SHAs. Internal action references use
`uses: $/.github/actions/<name>` to resolve the executing CI-tools commit;
do not replace these with independently pinned CI-tools references.

## Instruction index

Detailed policies live in `.github/instructions/`; do not duplicate them here.
Copilot applies matching `applyTo` rules. Other agents should read the relevant
files explicitly.

| Task | Instructions |
|------|--------------|
| Add or change a CI tool, installer, or dependency | [Adding tools](.github/instructions/adding-tools.instructions.md) |
| Review a change | [Code review](.github/instructions/code-review.instructions.md) |
| Review CI security or changed trust boundaries | [Security review](.github/instructions/security-review.instructions.md) |

## Validation

Use the shared lock's uv and pytest versions. Relevant commands:

```shell
uv lock --check --project .github/actions/setup-ci-tool/tooling
uv run --locked --only-group pytest --project .github/actions/setup-ci-tool/tooling pytest -c .github/actions/setup-ci-tool/tooling/pyproject.toml .github/actions/setup-ci-tool/tests -v
prek run --files <changed-files>
```

Run the smallest checks covering the change. Documentation-only changes need
the applicable hooks, not the Python test suite. Follow the existing
`.pre-commit-config.yaml`; do not introduce a second hook configuration.
