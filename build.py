#!/usr/bin/env python3
import platform, subprocess, sys, os, pathlib

# NOTE: This script intentionally does not use the utils helper library, since this is the build script and things may go horribly wrong.
# We do not have ANY context of the file structure, so yeah.

# Path variables at the top
PERIODICA_DIR = pathlib.Path(__file__).parent.resolve()
VENV_DIR = PERIODICA_DIR / "venv"
PYTHON_COMMAND = "python3"
VENV_PYTHON = VENV_DIR / "bin" / "python"
REQUIREMENTS_FILE = PERIODICA_DIR / "requirements.txt"
PYPROJECT_FILE = PERIODICA_DIR / "pyproject.toml"
PERIODICA_SCRIPT = PERIODICA_DIR / "periodica.sh"
BIN_PATH = pathlib.Path.home() / ".local" / "bin"
SYMLINK_TARGET = BIN_PATH / "periodica"
OS = platform.system()

if OS not in ["Linux", "Darwin"]:
    print(f"Unsupported OS: {OS}. This tool is for Unix-based systems only. Please follow README.md for Windows instructions.")
    sys.exit(0)

if not VENV_DIR.exists():
    print("Virtual environment not found. Creating one...")
    subprocess.run([PYTHON_COMMAND, "-m", "venv", str(VENV_DIR)], check=True)
else:
    print("Virtual environment already exists. Moving on...")

print("Upgrading pip just in case...")
subprocess.run([str(VENV_PYTHON), "-m", "pip", "install", "--upgrade", "pip"], check=True)

print("Installing project dependencies...")
if REQUIREMENTS_FILE.exists():
    subprocess.run([str(VENV_PYTHON), "-m", "pip", "install", "-r", str(REQUIREMENTS_FILE)], check=True, cwd=str(PERIODICA_DIR))
elif PYPROJECT_FILE.exists():
    subprocess.run([str(VENV_PYTHON), "-m", "pip", "install", "-e", "."], check=True, cwd=str(PERIODICA_DIR))
else:
    print("Neither requirements.txt nor pyproject.toml found. Aborting...")
    sys.exit(0)

source_display = str(PERIODICA_SCRIPT).replace(str(pathlib.Path.home()), "~")
print(f"Would you like this script to make a symlink from {source_display} -> ~/.local/bin/periodica?")
print("THIS STEP IS MANDATORY FOR STANDARD INSTALLATIONS TO MAKE IT WORK. If you do not want a symlink at all, type the N key and hit Enter. (Y/n)")
confirmation = input("> ").lower().strip()

if confirmation in ["n", "no"]:
    print("Alright! Just please make sure what you are doing. You may run this build script again anytime to create a symlink.")
    print(f"If you are following a custom install, run: ln -s {PERIODICA_SCRIPT} ~/.local/bin/periodica")
    sys.exit(0)
elif confirmation not in ["", "y", "yes"]:
    print("Invalid input. Please enter 'y', 'n', or press Enter for yes.")
    sys.exit(0)

try:
    if not PERIODICA_SCRIPT.exists():
        print(f"Launch script missing: {PERIODICA_SCRIPT}")
        sys.exit(0)
    os.chmod(PERIODICA_SCRIPT, 0o755)
    BIN_PATH.mkdir(parents=True, exist_ok=True)
    if SYMLINK_TARGET.exists():
        if SYMLINK_TARGET.is_symlink() and SYMLINK_TARGET.resolve() == PERIODICA_SCRIPT.resolve():
            print(f"Symlink already correctly set: {SYMLINK_TARGET} -> {PERIODICA_SCRIPT}")
        else:
            print(f"CLI entry already exists at: {SYMLINK_TARGET}")
            overwrite = input("Would you like to overwrite it? [y/N]: ").strip().lower()
            if overwrite != "y":
                print(f"Skipped creating symlink. Please do it manually: ln -s {PERIODICA_SCRIPT} ~/.local/bin/periodica")
                sys.exit(0)
            SYMLINK_TARGET.unlink()
            SYMLINK_TARGET.symlink_to(PERIODICA_SCRIPT)
            print(f"Symlink replaced: {SYMLINK_TARGET} -> {PERIODICA_SCRIPT}")
    else:
        SYMLINK_TARGET.symlink_to(PERIODICA_SCRIPT)
        print(f"Symlink created: {SYMLINK_TARGET} -> {PERIODICA_SCRIPT}")

    path_dirs = os.environ.get("PATH", "").split(os.pathsep)
    if str(BIN_PATH) not in path_dirs:
        print(f"Warning: {BIN_PATH} is not in your PATH. Add it with:")
        print(f"    echo 'export PATH=\"$HOME/.local/bin:$PATH\"' >> ~/.bashrc")
        print("    source ~/.bashrc")
        print("(Please make sure to place ~/.bashrc to any startup scripts of your shell)\nOnce this script finishes running, please run the command above to be able to access Periodica.")

except Exception as error:
    print(f"Failed to create symlink: {error}")
    sys.exit(0)

print("Setup complete. You can now run Periodica using: periodica")
