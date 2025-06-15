#!/usr/bin/env python3
import platform
import os
import subprocess
import sys

os_name = platform.system()

if os_name == "Windows":
    if "venv" not in os.listdir():
        print("Virtual environment was not found; let's create one!")
        subprocess.run(["python", "-m", "venv", "venv"], check=True)
    else:
        print("The virtual environment was found here already... but how?")

    print("Installing packages into the virtual environment...")
    subprocess.run(["venv\\Scripts\\python.exe", "-m", "pip", "install", "-r", "requirements.txt"], check=True)

    print("You're all set up! Now feel free to continue following instructions in the README.md file.")

elif os_name in ["Linux", "Darwin"]:
    if "venv" not in os.listdir():
        print("Virtual environment was not found; let's create one!")
        subprocess.run(["python3", "-m", "venv", "venv"], check=True)
    else:
        print("The virtual environment was found here already... but how?")

    print("Installing packages into the virtual environment...")
    subprocess.run(["venv/bin/python", "-m", "pip", "install", "-r", "requirements.txt"], check=True)

    print("You're all set up! Now feel free to continue following instructions in the README.md file.")
else:
    print(f"Uh oh! You are running this on an unexpected and unsupported OS: {os_name}")
    sys.exit(1)