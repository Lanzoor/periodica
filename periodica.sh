#!/bin/bash

SOURCE="${BASH_SOURCE[0]}"
while [ -L "$SOURCE" ]; do
  DIR="$(cd -P "$(dirname "$SOURCE")" && pwd)"
  SOURCE="$(readlink "$SOURCE")"
  [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE"
done
SCRIPT_DIR="$(cd -P "$(dirname "$SOURCE")" && pwd)"

cd "$SCRIPT_DIR" || exit 1

if [ ! -d venv ]; then
  echo "Virtual environment not found. Please run the build.py file."
  exit 1
fi

source "$SCRIPT_DIR/venv/bin/activate"
python3 "$SCRIPT_DIR/src/main.py" "$@"
deactivate
