#!/bin/bash

# Determine where the script is being runned
SOURCE="${BASH_SOURCE[0]}"
while [ -L "$SOURCE" ]; do
  DIR="$(cd -P "$(dirname "$SOURCE")" && pwd)"
  SOURCE="$(readlink "$SOURCE")"
  [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE"
done
SCRIPT_DIR="$(cd -P "$(dirname "$SOURCE")" && pwd)"

cd "$SCRIPT_DIR" || exit 1

# Activate the venv (that is, if it exists)
if [ -d "$SCRIPT_DIR/venv" ]; then
  source "$SCRIPT_DIR/venv/bin/activate"
fi

# Run the main script
python3 "$SCRIPT_DIR/src/main.py" "$@"

# Deactivate it (again, only if it exists)
if [ -n "$VIRTUAL_ENV" ]; then
  deactivate
fi
