#!/bin/bash
set -e
cd "$(dirname "$0")"

if [ ! -d "venv" ]; then
  echo "Creating a virtual environment for dependencies..."
  python3 -m venv venv
fi

echo "Activating virtual environment and installing dependencies..."
source venv/bin/activate
pip install -r requirements.txt
deactivate

echo "Done! Now feel free to follow the subsequent steps in execution."
