import tomllib, sys, subprocess, time, platform, pathlib
from utils.terminal import bold, fore, RED, BLUE
from utils.loader import Logger, get_response, failsafe
from utils.directories import PERIODICA_DIR, PYPROJECT_FILE, BUILD_SCRIPT

log = Logger(enable_debugging=False)

if __name__ == "__main__":
    print("Please refrain from running this script manually. Instead, please run the periodica.sh file with the --update flag.")
    sys.exit(0)
OS = platform.system()

if OS not in ["Linux", "Darwin"]:
    print("This tool is for Unix-based systems only. If you are on any unsupported system, please update them manually.")
    sys.exit(0)

try:
    from packaging import version
except ImportError:
    failsafe()

def fetch_toml():
    try:
        with open(PYPROJECT_FILE, "rb") as f:
            toml_data = tomllib.load(f)
    except PermissionError:
        print("Permission denied while reading pyproject.toml.")
        sys.exit(0)
    except FileNotFoundError:
        print("pyproject.toml not found. Please manually update if using version < v5.0.2-alpha.")
        sys.exit(0)

    local_version = toml_data.get("project", {}).get("version")
    if not local_version:
        print("Could not determine local version.")
        sys.exit(0)

    return local_version

def update_main():
    log.info("Update program initialized.")

    local_version = fetch_toml()
    url = "https://raw.githubusercontent.com/Lanzoor/periodictable/main/pyproject.toml"
    print(f"Getting content from {url}...")

    response = get_response(url)
    lts_toml = tomllib.loads(response.text)
    lts_version = lts_toml.get("project", {}).get("version")

    if not lts_version:
        print("Failed to get latest version info.")
        log.abort("Failed to get latest version info.")

    print(f"Local version: {local_version}")
    print(f"Latest version: {lts_version}")
    log.info(f"Local: {local_version}, latest: {lts_version}")

    try:
        parsed_local = version.parse(local_version)
        parsed_lts = version.parse(lts_version)
    except Exception:
        print(fore("Failed to parse version. Check if pyproject.toml is malformed.", RED))
        sys.exit(0)

    if parsed_local == parsed_lts:
        print(bold("You are using the latest version."))
        log.info("Scripts are up-to-date.")
        sys.exit(0)
    elif parsed_local > parsed_lts:
        print(bold("You are using a newer or development version.") + " Just please make sure that you didn't modify the pyproject.toml file.")
        log.warn("Scripts are in the development version. Please make sure to not tweak the pyproject.toml file if possible.")
        sys.exit(0)

    print(bold(f"Update available: {lts_version}!"))
    log.info(f"An update is avaliable; {lts_version}")

    print(
        f"This will forcefully update the repo from GitHub.\n"
        f"{fore('This won\'t delete your config.json, output.json, and any other files that are marked in .gitignore.', BLUE)}\n"
        "Do you want to continue? (Y/n)"
    )

    confirmation = input("> ").strip().lower()
    if confirmation not in ["y", "yes", ""]:
        print("Update canceled.")
        log.abort("User canceled update confirmation.")

    try:
        subprocess.run(["git", "fetch"], cwd=PERIODICA_DIR, check=True)
        subprocess.run(["git", "reset", "--hard", "origin/main"], cwd=PERIODICA_DIR, check=True)
        print(bold("Successfully pulled the latest changes. Let's build it up for you once again..."))
        time.sleep(2)

        if not BUILD_SCRIPT.exists():
            print("build.py not found. Aborting...")
            sys.exit(0)

        print("Running build.py to reinitialize environment...")
        subprocess.run([sys.executable, str(BUILD_SCRIPT)], check=True)

        print(bold("Update complete."))
        sys.exit(0)

    except subprocess.CalledProcessError:
        print(fore("Git fetch/reset or build failed. Please ensure this is a valid Git repository.", RED))
        log.abort("Failed to fetch and/or reset. Ensure this is a valid Git repository.")
