import importlib.util
from pathlib import Path

import pytest


SPEC = importlib.util.spec_from_file_location(
    "tool_inventory", Path(__file__).resolve().parents[1] / "tool_inventory.py"
)
inventory = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(inventory)


def test_reads_existing_pins_and_deduplicates_installers(tmp_path, monkeypatch):
    files = {
        inventory.CATALOG: (Path(__file__).resolve().parents[1] / "native_tools.toml").read_text(encoding="utf-8"),
        ".github/workflows/reusable-pixi-lock_diff.yml": (
            "default: v0.67.2\nPIXI_DIFF_VERSION: 0.1.8\nPIXI_DIFF_TO_MARKDOWN_VERSION: 0.3.9\n"
        ),
        ".github/actions/reusable-python-setup_conda/action.yml": "micromamba_version=2.1.0-0",
        ".github/workflows/reusable-python-publish_rattler_package.yml": "rattler-build-version: 'v0.74.0'",
        ".github/workflows/jfrog.yml": f"jfrog/setup-jfrog-cli@{'a' * 40}\njfrog/setup-jfrog-cli@{'a' * 40}",
    }
    for name, content in files.items():
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    calls = []
    monkeypatch.setattr(
        inventory, "installer_version", lambda installer, ref, pattern: calls.append((installer, ref)) or "2.127.0"
    )
    first = inventory.tool_versions(tmp_path)
    assert len(first) == 6
    assert calls == [("jfrog/setup-jfrog-cli", "a" * 40)]
    assert "pkg:conda/pixi-diff@0.1.8?channel=conda-forge" in first
    assert "pkg:github/jfrog/jfrog-cli@v2.127.0" in first
    path = tmp_path / ".github/workflows/reusable-pixi-lock_diff.yml"
    path.write_text(files[".github/workflows/reusable-pixi-lock_diff.yml"].replace("0.1.8", "0.1.9"), encoding="utf-8")
    assert first - inventory.tool_versions(tmp_path) == {"pkg:conda/pixi-diff@0.1.8?channel=conda-forge"}


def test_new_catalog_entry_is_collected_without_code_changes(tmp_path):
    path = tmp_path / inventory.CATALOG
    path.parent.mkdir(parents=True)
    path.write_text(
        """schema = 1
[[tools]]
name = "Example tool"
package = "pkg:conda/example-tool"
advisories = "example/security"
source = ".github/new-tool.yml"
pattern = 'version: (\\d+\\.\\d+\\.\\d+)'
qualifiers = "channel=conda-forge"
""",
        encoding="utf-8",
    )
    (tmp_path / ".github/new-tool.yml").write_text("version: 1.2.3", encoding="utf-8")
    assert inventory.tool_versions(tmp_path) == {"pkg:conda/example-tool@1.2.3?channel=conda-forge"}


@pytest.mark.parametrize("field,value", [
    ("source", "../private/file.yml"),
    ("advisories", "example/security?state=all"),
    ("releases", "example/releases?state=all"),
])
def test_rejects_catalog_paths_or_repository_injection(tmp_path, field, value):
    text = (Path(__file__).resolve().parents[1] / "native_tools.toml").read_text(encoding="utf-8")
    replacement = {
        "source": ".github/workflows/reusable-pixi-lock_diff.yml",
        "advisories": "prefix-dev/pixi",
        "releases": "mamba-org/micromamba-releases",
    }[field]
    text = text.replace(f'{field} = "{replacement}"', f'{field} = "{value}"', 1)
    path = tmp_path / inventory.CATALOG
    path.parent.mkdir(parents=True)
    path.write_text(text, encoding="utf-8")
    with pytest.raises(ValueError):
        inventory.load_tools(tmp_path)


@pytest.mark.parametrize("text", ["default: latest", "default: 1.2.3\ndefault: 2.3.4"])
def test_rejects_missing_or_ambiguous_fixed_versions(text):
    with pytest.raises(ValueError, match="Expected one fixed tool version"):
        inventory.version(r"^default: (\d+\.\d+\.\d+)$", text)


def test_inventory_is_direct_and_does_not_replace_native_manifests():
    environment = {
        "GITHUB_SHA": "a" * 40,
        "GITHUB_REF": "refs/heads/main",
        "GITHUB_RUN_ID": "42",
        "GITHUB_SERVER_URL": "https://github.com",
        "GITHUB_REPOSITORY": "MiraGeoscience/CI-tools",
    }
    purl = "pkg:github/prefix-dev/pixi@v0.67.2"
    snapshot = inventory.build_snapshot({purl}, environment)
    manifest = next(iter(snapshot["manifests"].values()))
    assert "file" not in manifest
    assert manifest["metadata"]["transitive-coverage"] is False
    assert manifest["resolved"][purl] == {
        "package_url": purl, "relationship": "direct", "scope": "development",
    }
    with pytest.raises(ValueError, match="Empty native tool inventory"):
        inventory.build_snapshot(set(), environment)
