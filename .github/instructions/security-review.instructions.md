---
applyTo: ".github/actions/**,.github/workflows/**,.github/dependabot.yml"
---

# CI security review

Use this checklist for security reviews; during implementation, apply it to
the trust boundaries affected by the change rather than auditing unrelated code.

Check untrusted event data entering shell commands, credential handling,
checkout refs, fork pull requests, artifact provenance, and action permissions.
Use minimum required token permissions. Keep privileged dependency submission
on trusted default-branch commits, not untrusted pull-request code.

Distinguish pinned actions from their runtime downloads and defaults. Follow
[adding-tools.instructions.md](adding-tools.instructions.md) to verify tool
ownership, exact versions, collection tests, and documented exclusions.

Dependency graph visibility, CVE alert matching, transitive coverage, and
automatic version updates are separate properties. The current GitHub release
and Conda native inventory does not provide general CVE alerts for the direct
native tools or their bundled dependencies. Alerts require matching supported
package identities and GitHub-reviewed advisories; see the README.

Report concrete vulnerabilities with the exploitation path, affected files and
lines, severity, and confidence. Separate hardening suggestions and tracking
gaps from vulnerabilities. State explicitly when no vulnerabilities were found
and identify validation limits; do not imply inventory or linting is a full audit.

Leave repository security settings unchanged unless explicitly requested.
