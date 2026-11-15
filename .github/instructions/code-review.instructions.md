---
applyTo: "**"
excludeAgent: "cloud-agent"
---

# Code review

Apply this checklist when reviewing a change. Report actionable correctness
and behavior issues with affected files, lines, impact, and supporting evidence;
avoid speculative findings and trivial style comments.

Check reusable workflow and action inputs, outputs, permissions, and defaults
against their callers. Preserve intended behavior and the caller's environment.
Verify directly dependent call sites, appropriate pytest cases, and CI path
filters. Keep unrelated refactoring separate from behavior changes.

For new or changed installers, follow
[adding-tools.instructions.md](adding-tools.instructions.md). Flag uncovered
CI-tools-owned tools, floating installations, duplicate pins, missing collection
tests, and undocumented exclusions as required changes.

For CI trust-boundary concerns, use
[security-review.instructions.md](security-review.instructions.md). Missing
inventory coverage is not automatically an exploitable vulnerability, and
passing inventory tests is not proof of CVE alert coverage.

State checks performed and any unverified claims. Do not modify code, create
findings files, or commit review results unless requested.
