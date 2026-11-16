---
applyTo: ".github/actions/**,.github/workflows/**,.github/dependabot.yml"
---

# Adding or changing CI tools

Inspect setup actions, package-manager commands, binary downloads, and shell
installers to identify the tools they install. A pinned action SHA alone does
not make its installed tool auditable or automatically updateable.

## Required tracking

Every CI-tools-owned tool must use one of these paths:

- PyPI: declare a dependency group named after the primary
  package in `.github/actions/setup-ci-tool/tooling/pyproject.toml`, commit its
  exact `uv.lock`, and use `setup-ci-tool` to install it or resolve its version.
  Choose patch-only or patch-and-minor updates per tool, based on compatibility
  guarantees and CI impact; do not assume minor releases are nonbreaking,
  especially before 1.0. Express that choice in manifest constraints and keep
  Dependabot's `lockfile-only` strategy so constraint changes require manual
  review, while retaining exact installation locks.
- Other tools: declare the package identity, verified advisory repository,
  release repository when different, and actual production pin source in
  `.github/actions/setup-ci-tool/native_tools.toml`. Keep version pins in the
  production installer files, not in this catalog. Extend collection tests
  in the same change.
  Inventory submission and private DevOps monitoring both consume this catalog.
  Release monitoring defaults to the advisory repository unless `releases`
  overrides it.
  Native installers also call `record-native-tools` after installation for
  caller inventories. Supply the existing fixed pin, or add a `version_command`
  executable and optional `runtime_prefix` in the catalog to resolve the CLI's
  `--version` output. Do not duplicate pins. DevOps reads this metadata as data;
  it never executes the catalog commands.
  New entries using the existing extraction rules need no separate DevOps
  tool-list change; a new catalog schema or extraction mechanism requires
  updating both consumers and their tests.

Use uv to update the lock. Keep the Dependabot uv entry pointed at the shared
tooling directory. Do not introduce parallel locks or duplicate version pins.
The native inventory reads existing pins; keep it small.

CLI tools must remain isolated from the caller's Python. For libraries, use
the action's `python-path` output instead of activating its environment or
adding it to the caller's PATH.

Caller-owned test dependencies, build backends, and hook environments belong
in the calling repository's manifests. Document the ownership and reason for
any caller-owned or runner-provided exclusion; do not silently exempt tools.

## Validation and coverage claims

Collection tests must exercise the new tool, not merely assert its version
constant. Add new inventory source files to `ci-tool-tests.yml` path filters
so changes to those files trigger tests.

Verify package identity, alert support, and update support separately. Record
limitations in the README. Do not map an unrelated package to a native tool
or claim CVE coverage from a GitHub release or Conda inventory entry.

GitHub's native Dependabot graph jobs provide uv dependency coverage. Do not
submit competing snapshots for the uv manifest or native action/workflow
manifests. Native version inventory is neither transitive audit coverage nor
an automatic updater.

Tool discovery is a required implementation and review check, not an automatic
CI gate: both operations cover only explicitly cataloged tool families.
