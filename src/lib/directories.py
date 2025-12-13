import pathlib, sys

if getattr(sys, "frozen", False):
    # PyInstaller support
    PERIODICA_DIR = pathlib.Path(sys._MEIPASS) # type: ignore
else:
    PERIODICA_DIR = pathlib.Path(__file__).resolve().parent.parent.parent # type: ignore

# Paths to scripts / files
BUILD_SCRIPT = PERIODICA_DIR / "build.py"
VENV_DIR = PERIODICA_DIR / "venv"
VENV_PYTHON = VENV_DIR / "bin" / "python"
REQUIREMENTS_FILE = PERIODICA_DIR / "requirements.txt"
PYPROJECT_FILE = PERIODICA_DIR / "pyproject.toml"
PERIODICA_SCRIPT = PERIODICA_DIR / "periodica.sh"
MAIN_SCRIPT = PERIODICA_DIR / "src" / "main.py"
UPDATE_SCRIPT = PERIODICA_DIR / "src" / "update.py"

ELEMENT_DATA_FILE = PERIODICA_DIR / "src" / "elements.json"
ISOTOPE_DATA_FILE = PERIODICA_DIR / "src" / "isotopes.json"

RUNTIME_DIR = pathlib.Path.home() / ".periodica"
RUNTIME_DIR.mkdir(exist_ok=True)
OUTPUT_FILE = RUNTIME_DIR / "output.json"
LOGGING_FILE = RUNTIME_DIR / "execution.log"
