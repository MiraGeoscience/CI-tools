import typer
from packaging.version import parse

app = typer.Typer()

def _is_publishable(version_string: str) -> bool:
    """
    Checks if a version string is publishable.
    Returns False for alpha 0 releases and dev versions.
    """
    v = parse(version_string)
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
    print(f"Normalized version: {parse(version)}")

@app.command()
def publishable(version: str):
    """
    Check if a version is publishable.

    Print whether the version is publishable,
    and exit with code 0 if it is, or code 1 if it is not.
    """
    result = _is_publishable(version)
    if result:
        print(f"Version {version} is publishable.")
        raise typer.Exit(code=0)
    else:
        print(f"Version {version} is NOT publishable.")
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app()
