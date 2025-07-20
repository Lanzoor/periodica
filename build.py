#!/usr/bin/env python3
import platform
import subprocess
import sys
import os
from pathlib import Path

# Path variables at the top
script_dir = Path(__file__).parent.resolve()
venv_path = script_dir / "venv"
py_cmd = "python3"
venv_python = venv_path / "bin" / "python"
requirements = script_dir / "requirements.txt"
pyproject = script_dir / "pyproject.toml"
sh_script = script_dir / "periodica.sh"
bin_path = Path.home() / ".local" / "bin"
symlink_target = bin_path / "periodica"

OS = platform.system()
if OS not in ["Linux", "Darwin"]:
    print(f"Unsupported OS: {OS}. This tool is for Unix-based systems only. Please follow README.md for Windows instructions.")
    sys.exit(0)

if not venv_path.exists():
    print("Virtual environment not found. Creating one...")
    subprocess.run([py_cmd, "-m", "venv", str(venv_path)], check=True)
else:
    print("Virtual environment already exists. Moving on...")

print("Upgrading pip just in case...")
subprocess.run([str(venv_python), "-m", "pip", "install", "--upgrade", "pip"], check=True)

print("Installing project dependencies...")
if requirements.exists():
    subprocess.run([str(venv_python), "-m", "pip", "install", "-r", str(requirements)], check=True, cwd=str(script_dir))
elif pyproject.exists():
    subprocess.run([str(venv_python), "-m", "pip", "install", "-e", "."], check=True, cwd=str(script_dir))
else:
    print("Neither requirements.txt nor pyproject.toml found. Aborting...")
    sys.exit(0)

source_display = str(sh_script).replace(str(Path.home()), "~")
print(f"Would you like this script to make a symlink from {source_display} -> ~/.local/bin/periodica?")
print("THIS STEP IS MANDATORY FOR STANDARD INSTALLATIONS TO MAKE IT WORK. If you do not want a symlink at all, type the N key and hit Enter. (Y/n)")
confirmation = input("> ").lower().strip()

if confirmation == "n":
    print("Alright! Just please make sure what you are doing. You may run this build script again anytime to create a symlink.")
    print(f"If you are following a custom install, run: ln -s {sh_script} ~/.local/bin/periodica")
    sys.exit(0)
elif confirmation not in ["", "y"]:
    print("Invalid input. Please enter 'y', 'n', or press Enter for yes.")
    sys.exit(0)

try:
    if not sh_script.exists():
        print(f"Launch script missing: {sh_script}")
        sys.exit(0)
    os.chmod(sh_script, 0o755)
    bin_path.mkdir(parents=True, exist_ok=True)
    if symlink_target.exists():
        if symlink_target.is_symlink() and symlink_target.resolve() == sh_script.resolve():
            print(f"Symlink already correctly set: {symlink_target} -> {sh_script}")
        else:
            print(f"CLI entry already exists at: {symlink_target}")
            overwrite = input("Would you like to overwrite it? [y/N]: ").strip().lower()
            if overwrite != "y":
                print(f"Skipped creating symlink. Please do it manually: ln -s {sh_script} ~/.local/bin/periodica")
                sys.exit(0)
            symlink_target.unlink()
            symlink_target.symlink_to(sh_script)
            print(f"Symlink replaced: {symlink_target} -> {sh_script}")
    else:
        symlink_target.symlink_to(sh_script)
        print(f"Symlink created: {symlink_target} -> {sh_script}")

    path_dirs = os.environ.get("PATH", "").split(os.pathsep)
    if str(bin_path) not in path_dirs:
        print(f"Warning: {bin_path} is not in your PATH. Add it with:")
        print(f"    echo 'export PATH=\"$HOME/.local/bin:$PATH\"' >> ~/.bashrc")
        print("    source ~/.bashrc")
        print("Once this script finishes running, please run the command above to be able to access Periodica.")

except Exception as error:
    print(f"Failed to create symlink: {error}")
    sys.exit(0)

print("Setup complete. You can now run Periodica using: periodica")
