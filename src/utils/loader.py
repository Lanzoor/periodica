import json, logging, time, sys, subprocess
from utils.directories import LOGGING_FILE, VENV_DIR, PERIODICA_DIR, BUILD_SCRIPT

with open(LOGGING_FILE, 'w', encoding="utf-8"):
    pass

logging.basicConfig(
    filename=LOGGING_FILE,
    filemode='w',
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    force=True
)

class Logger():
    def __init__(self, *, enable_debugging=False):
        self.enable_debugging = enable_debugging

    def debug(self, message):
        from .terminal import bold
        logging.debug(message)
        if self.enable_debugging:
            print(bold("DEBUG: " + message))

    def info(self, message):
        from .terminal import fore, GREEN
        logging.info(message)
        if self.enable_debugging:
            print(fore("INFO: " + message, GREEN))

    def warn(self, message):
        from .terminal import fore, YELLOW
        logging.warning(message)
        if self.enable_debugging:
            print(fore("WARNING: " + message, YELLOW))

    def error(self, message):
        from .terminal import fore, RED
        logging.error(message)
        if self.enable_debugging:
            print(fore("ERROR: " + message, RED))

    def fatal(self, message):
        from .terminal import fore, BLUE
        logging.fatal(message)
        if self.enable_debugging:
            print(fore("FATAL: " + message, BLUE))

    def abort(self, message):
        self.error(message)
        time.sleep(1)
        self.fatal("Program terminated.")
        sys.exit(0)

log = Logger(enable_debugging=False)

default_config = {
    "use_unicode": True,
    "terminal_effects": True,
    "isotope_format": "fullname-number",
    "animation_type": "none",
    "animation_delay": 0.0005,
    "constant_debugging": False,
    "default_sorting_method": "ascending"
}

valid_formats = ["fullname-number", "symbol-number", "numbersymbol", "number-symbol"]
valid_animation_types = ["char", "line", "none"]
valid_sorting_methods = ["ascending", "descending", "name"]

_config = None

def get_config():
    global _config
    if _config is not None:
        return _config

    try:
        with open(PERIODICA_DIR / "src" / "config.json", "r", encoding="utf-8") as file:
            _config = json.load(file)
    except (json.JSONDecodeError, FileNotFoundError):
        _config = default_config.copy()
        save_config()

    for key, default in default_config.items():
        if key == "isotope_format" and _config.get(key) not in valid_formats:
            _config[key] = default
        elif key == "animation_type" and _config.get(key) not in valid_animation_types:
            _config[key] = default
        elif key == "default_sorting_method" and _config.get(key) not in valid_sorting_methods:
            _config[key] = default
        else:
            _config.setdefault(key, default)

    return _config

def save_config():
    global _config
    with open(PERIODICA_DIR / "src" / "config.json", "w", encoding="utf-8") as file:
        json.dump(_config or default_config, file, indent=4)

def get_response(url: str):
    try:
        import requests
    except ImportError:
        import_failsafe()

    import requests
    try:
        response = requests.get(url)
        response.raise_for_status()
        print(f"HTTP status code: {response.status_code} (pass)")
        return response
    except requests.exceptions.ConnectionError:
        print("Whoops! There was a network connection error. Please check your network connection, and try again later.")
        log.abort("Couldn't proceed; failed to connect to page.")
    except requests.exceptions.HTTPError:
        print(f"Failed to download data! HTTP status code: {response.status_code}")
        log.abort(f"Failed to fetch data. Status code: {response.status_code}.")

def import_failsafe():
    if not VENV_DIR.is_dir():
        print("The virtual environment was not found. Should I run the build script for you? (Y/n)")

        confirmation = input("> ").strip().lower()
        if confirmation not in ["y", "yes", ""]:
            print("You denied the file execution. Please run the build script yourself.")
            sys.exit(0)
        if BUILD_SCRIPT.is_file():
            subprocess.run([sys.executable, str(BUILD_SCRIPT)], check=True)
            sys.exit(0)
        else:
            print("The build script was not found. Please read the README.md for more information. (If that even exists, that is.)")
            sys.exit(0)

