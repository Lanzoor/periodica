import tomllib, sys, subprocess, time
from pathlib import Path
from utils import animate_print, bold, fore, RED, get_response, abort_program
from utils.loader import logging

try:
    from packaging import version
except ImportError:
    animate_print("Whoopsies, the packaging module was not found in your environment! Please read the README.md file for more information.")
    abort_program("Couldn't proceed; the packaging library was not found in the environment.")

def update_main():
    logging.info("Update program initialized.")

    project_root = Path(__file__).resolve().parent.parent
    pyproject_path = project_root / "pyproject.toml"

    try:
        with open(pyproject_path, "rb") as f:
            toml_data = tomllib.load(f)
    except PermissionError:
        animate_print("Permission denied while reading pyproject.toml.")
        sys.exit(1)
    except FileNotFoundError:
        animate_print("pyproject.toml not found. Please manually update if using version < v5.0.2-alpha.")
        sys.exit(1)

    local_version = toml_data.get("project", {}).get("version")
    if not local_version:
        animate_print("Could not determine local version.")
        sys.exit(1)

    url = "https://raw.githubusercontent.com/Lanzoor/periodictable/main/pyproject.toml"
    animate_print(f"Getting content from {url}...")

    response = get_response(url)
    lts_toml = tomllib.loads(response.text)
    lts_version = lts_toml.get("project", {}).get("version")

    if not lts_version:
        animate_print("Failed to get latest version info.")
        sys.exit(1)

    animate_print(f"Local version: {local_version}")
    animate_print(f"Latest version: {lts_version}")

    local_version = version.parse(local_version)
    lts_version = version.parse(lts_version)

    if local_version == lts_version:
        animate_print(bold("You are using the latest version."))
        sys.exit(0)
    if local_version > lts_version:
        animate_print(bold("You are using the nightly version. (in development, you probably either modified pyproject.toml or you are the developer)"))
        sys.exit(0)

    animate_print(bold(f"Update available: {lts_version}!"))
    animate_print(f"This will pull the latest source code from GitHub. Proceed?\n{fore("Warning! This will delete your config.json file. Backup it if you want.", RED)} (Y/n)")

    confirmation = input("> ").strip().lower()
    if confirmation not in ["y", "yes", ""]:
        animate_print("Update canceled.")
        sys.exit(0)

    try:
        subprocess.run(["git", "pull"], cwd=project_root, check=True)
        animate_print(bold("Successfully pulled the latest changes. Let's build it up for you once again..."))
        time.sleep(2)

        build_script = project_root / "build.py"
        animate_print("Running build.py to reinitialize environment...")
        subprocess.run([sys.executable, str(build_script)], check=True)

        animate_print(bold("Update complete."))
        sys.exit(0)

    except subprocess.CalledProcessError:
        animate_print(fore("Git pull or build failed. This may not be a valid repository. Make sure you are in the right directory, and use git pull to try manually.", RED))
        sys.exit(1)

if __name__ == "__main__":
    animate_print(fore("Please do not run this script directly. Use main.py with the --update flag.", RED))
    sys.exit(0)
