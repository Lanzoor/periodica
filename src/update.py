import tomllib, sys, subprocess, time, platform, pathlib
from utils.terminal import animate_print, bold, fore, RED, BLUE
from utils.loader import Logger, get_response

PERIODICA_DIR = pathlib.Path(__file__).resolve().parent.parent
PYPROJECT_FILE = PERIODICA_DIR / "pyproject.toml"
BUILD_FILE = PERIODICA_DIR / "build.py"

log = Logger(debug=False)

if __name__ == "__main__":
    animate_print("Please refrain from running this script manually. Instead, please run the periodica.sh file with the --update flag.")
    sys.exit(0)

OS = platform.system()

if OS not in ["Linux", "Darwin"]:
    animate_print("This tool is for Unix-based systems only. If you are on Windows, please get them manually.")
    sys.exit(0)

try:
    from packaging import version
except ImportError:
    animate_print("Whoopsies, the packaging module was not found in your environment! Please read the README.md file for more information.")
    log.abort("Couldn't proceed; the packaging library was not found in the environment.")

def update_main():
    log.info("Update program initialized.")

    try:
        with open(PYPROJECT_FILE, "rb") as f:
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
        log.abort("Failed to get latest version info.")

    animate_print(f"Local version: {local_version}")
    animate_print(f"Latest version: {lts_version}")
    log.info(f"Local: {local_version}, latest: {lts_version}")

    try:
        parsed_local = version.parse(local_version)
        parsed_lts = version.parse(lts_version)
    except Exception:
        animate_print(fore("Failed to parse version. Check if pyproject.toml is malformed.", RED))
        sys.exit(1)

    if parsed_local == parsed_lts:
        animate_print(bold("You are using the latest version."))
        log.info("Scripts are up-to-date.")
        sys.exit(0)
    elif parsed_local > parsed_lts:
        animate_print(bold("You are using a newer or development version.") + " Just please make sure that you didn't modify the pyproject.toml file.")
        log.warn("Scripts are in the development version. Please make sure to not tweak the pyproject.toml file if possible.")
        sys.exit(0)

    animate_print(bold(f"Update available: {lts_version}!"))
    log.info(f"An update is avaliable; {lts_version}")

    animate_print(
        f"This will forcefully update the repo from GitHub.\n"
        f"{fore('This won\'t delete your config.json, output.json, and any other files that are marked in .gitignore.', BLUE)}\n"
        "Do you want to continue? (Y/n)"
    )

    confirmation = input("> ").strip().lower()
    if confirmation not in ["y", "yes", ""]:
        animate_print("Update canceled.")
        log.abort("User canceled update confirmation.")

    try:
        subprocess.run(["git", "fetch"], cwd=PERIODICA_DIR, check=True)
        subprocess.run(["git", "reset", "--hard", "origin/main"], cwd=PERIODICA_DIR, check=True)
        animate_print(bold("Successfully pulled the latest changes. Let's build it up for you once again..."))
        time.sleep(2)

        animate_print("Running build.py to reinitialize environment...")
        subprocess.run([sys.executable, str(BUILD_FILE)], check=True)

        animate_print(bold("Update complete."))
        sys.exit(0)

    except subprocess.CalledProcessError:
        animate_print(fore("Git fetch/reset or build failed. Please ensure this is a valid Git repository.", RED))
        log.abort("Failed to fetch and/or reset. Ensure this is a valid Git repository.")
