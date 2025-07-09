#!/usr/bin/env python3
import platform
import subprocess
import sys
from pathlib import Path

script_dir = Path(__file__).parent.resolve()

OS = platform.system()
venv_path = script_dir / "venv"

if OS not in ["Linux", "Darwin"]:
    print(f"This tool is for Unix-based systems only. Please follow the README.md instructions if running on Windows, instead of this script. Unsupported OS: {OS}")
    sys.exit(1)

py_cmd = "python3"
venv_python = venv_path / "bin" / "python"

if not venv_path.exists():
    print("Virtual environment was not found. Creating one...")
    subprocess.run([py_cmd, "-m", "venv", str(venv_path)], check=True)
else:
    print("Virtual environment already exists. Moving on...")

print("Upgrading pip just in case...")
subprocess.run([str(venv_python), "-m", "pip", "install", "--upgrade", "pip"], check=True)

print("Installing project dependencies...")
requirements = script_dir / "requirements.txt"
pyproject = script_dir / "pyproject.toml"

if requirements.exists():
    subprocess.run([str(venv_python), "-m", "pip", "install", "-r", str(requirements)],
                check=True, cwd=str(script_dir))
elif pyproject.exists():
    subprocess.run([str(venv_python), "-m", "pip", "install", "-e", "."],
                check=True, cwd=str(script_dir))
else:
    print("Neither requirements.txt nor pyproject.toml found. Aborting...")
    sys.exit(1)

bin_path = Path.home() / ".local" / "bin"
bin_path.mkdir(parents=True, exist_ok=True)

sh_script = script_dir / "periodica.sh"
symlink_target = bin_path / "periodica"

try:
    if not sh_script.exists():
        print(f"Launch script missing: {sh_script}")
    else:
        if symlink_target.exists() or symlink_target.is_symlink():
            if symlink_target.is_symlink():
                current_target = symlink_target.resolve()
                if current_target != sh_script.resolve():
                    print(f"CLI entry already exists and points somewhere else: {symlink_target}")
                    overwrite = input("Would you like to overwrite it? [y/N]: ").strip().lower()
                    if overwrite == "y":
                        symlink_target.unlink()
                        symlink_target.symlink_to(sh_script)
                        print(f"Symlink replaced: {symlink_target} -> {sh_script}")
                    else:
                        print("Skipped creating symlink. Please do it manually")
                else:
                    print(f"Symlink already correctly set: {symlink_target} -> {sh_script}")
            else:
                print(f"A non-symlink file or directory already exists at: {symlink_target}")
                print("Please remove it manually if you want to link Periodica here.")
        else:
            try:
                symlink_target.symlink_to(sh_script)
                print(f"Symlink created: {symlink_target} -> {sh_script}")
            except Exception as symlink_error:
                print(f"Could not create symlink: {symlink_error}")

except Exception as error:
    print(f"Failed to create symlink: {error}")

print("Setup complete. You can now run Periodica using: periodica")
