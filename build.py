#!/usr/bin/env python3
import platform
import subprocess
import sys
from pathlib import Path

script_dir = Path(__file__).parent.resolve()

OS = platform.system()
venv_path = script_dir / "venv"

if OS == "Windows":
    py_cmd = "python"
    venv_python = venv_path / "Scripts" / "python.exe"
elif OS in ["Linux", "Darwin"]:
    py_cmd = "python3"
    venv_python = venv_path / "bin" / "python"
else:
    print(f"Unsupported OS: {OS}. Aborting...")
    sys.exit(1)

if not venv_path.exists():
    print("Virtual environment was not found. Creating one...")
    subprocess.run([py_cmd, "-m", "venv", str(venv_path)], check=True)
else:
    print("Virtual environment already exists. Moving on...")

print("Upgrading pip... (just in case something goes wrong)")
subprocess.run([str(venv_python), "-m", "pip", "install", "--upgrade", "pip"], check=True)

print("Installing project dependencies...")

requirements = script_dir / "requirements.txt"
pyproject = script_dir / "pyproject.toml"

if requirements.exists():
    subprocess.run([str(venv_python), "-m", "pip", "install", "-r", str(requirements)], check=True, cwd=str(script_dir))
elif pyproject.exists():
    subprocess.run([str(venv_python), "-m", "pip", "install", "-e", "."], check=True, cwd=str(script_dir))
else:
    print("Neither requirements.txt nor pyproject.toml found. Please make sure you got the right files.")
    sys.exit(1)

print("\nSetup complete! Now feel free to continue the installation process.")
