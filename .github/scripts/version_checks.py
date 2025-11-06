import sys
import typer
from packaging.version import parse, InvalidVersion

app = typer.Typer()

def _parse_or_exit(version_string: str):
    """
    Parse a version string, exiting if invalid.
    """
    try:
        return parse(version_string)
    except InvalidVersion:
        print(f"Invalid version string: {version_string}", file=sys.stderr)
        raise typer.Exit(1)

def _is_publishable(version_string: str) -> bool:
    """
    Checks if a version string is publishable.
    Returns False for alpha 0 releases and dev versions.
    """
    v = _parse_or_exit(version_string)
    if not v.is_prerelease:
        return True

    if v.pre and v.pre[0] == 'a' and v.pre[1] == 0:
        return False

    if v.dev:
        return False

    return True

@app.command()
def normalize(version: str):
    """
    Prints the normalized version string.
    """
    print(f"Normalized version: {_parse_or_exit(version)}")

@app.command()
def publishable(version: str):
    """
    Check if a version is publishable.

    Print "yes" or "no" depending on whether the version is publishable.
    """
    result = _is_publishable(version)
    print("yes" if result else "no")

if __name__ == "__main__":
    app()
