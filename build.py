#!/usr/bin/env python3
import os
import platform
import subprocess
import sys

OS = platform.system()
venv_path = "venv"

if OS == "Windows":
    py_cmd = "python"
    venv_python = os.path.join(venv_path, "Scripts", "python.exe")
elif OS in ["Linux", "Darwin"]:
    py_cmd = "python3"
    venv_python = os.path.join(venv_path, "bin", "python")
else:
    print(f"Unsupported OS: {OS}. Aborting...")
    sys.exit(1)

if not os.path.exists(venv_path):
    print("Virtual environment was not found. Creating one...")
    subprocess.run([py_cmd, "-m", "venv", venv_path], check=True)
else:
    print("Virtual environment already exists. Moving on...")

print("Upgrading pip... (just in case something goes wrong)")
subprocess.run([venv_python, "-m", "pip", "install", "--upgrade", "pip"], check=True)

print("Installing project dependencies...")

if os.path.exists("requirements.txt"):
    subprocess.run([venv_python, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
elif os.path.exists("pyproject.toml"):
    subprocess.run([venv_python, "-m", "pip", "install", "-e", "."], check=True)
else:
    print("Neither requirements.txt nor pyproject.toml found. Please make sure you got the right files.")
    sys.exit(1)

print("\nSetup complete! Now feel free to continue the installation process.")
