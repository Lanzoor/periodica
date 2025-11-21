import pathlib

# Directory paths and variables (if you forget this file then you are cooked.)
PERIODICA_DIR = pathlib.Path(__file__).resolve().parent.parent.parent
BUILD_SCRIPT = PERIODICA_DIR / "build.py"
VENV_DIR = PERIODICA_DIR / "venv"
# VENV_PYTHON = VENV_PATH / "bin" / "python"
# REQUIREMENTS_FILE = PERIODICA_DIR / "requirements.txt"
PYPROJECT_FILE = PERIODICA_DIR / "pyproject.toml"
# PERIODICA_SCRIPT = PERIODICA_DIR / "periodica.sh"
OUTPUT_FILE = PERIODICA_DIR / "src" / "output.json"
ELEMENT_DATA_FILE = PERIODICA_DIR / "src" / "elements.json"
ISOTOPE_DATA_FILE = PERIODICA_DIR / "src" / "isotopes.json"
CONFIG_SCRIPT = PERIODICA_DIR / "src" / "configuration.py"
UPDATE_SCRIPT = PERIODICA_DIR / "src" / "update.py"
LOGGING_FILE = PERIODICA_DIR / "src" / "execution.log"
MAIN_SCRIPT = PERIODICA_DIR / "src" / "main.py"
