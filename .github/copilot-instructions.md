# CI dependency tracking

GitHub Actions are welcome; pin third-party actions to full commit SHAs.
An action SHA or a fixed tool-version input does not, by itself, make the
installed tool a dependency that Dependabot can update or audit.

Declare CI-tools-owned PyPI tools with patch-compatible version constraints in
`.github/actions/setup-ci-tool/tooling/pyproject.toml`, using a dependency group
named after the primary package. Commit the corresponding exact `uv.lock`
and keep the Dependabot `uv` entry pointed at that directory. Use uv to update
the lock; do not introduce a parallel lockfile or duplicate version pins.

Use `setup-ci-tool` to install tools or obtain versions for existing actions.
Do not duplicate package versions in workflow inputs or download commands.
CLI tools must remain isolated from the caller's Python. For libraries, use
the action's `python-path` output instead of activating its environment.

Use GitHub-supported manifests and locks so dependency versions reach its
dependency graph without custom submission. GitHub's built-in Dependabot graph
jobs support uv and run automatically when the dependency graph is enabled.
Verify audit support separately from update support, and leave repository
security settings unchanged unless explicitly requested.
Do not misrepresent an unrelated package as a native tool just to obtain
Dependabot coverage. Document unsupported native tools in the README.

Caller-owned test dependencies, build backends, and hook environments belong
in the calling repository's manifests, not the CI-tools tooling manifest.
