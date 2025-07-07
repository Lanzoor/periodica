import json, logging, time, sys, pathlib

# utils -> src -> periodica, three parents
PERIODICA_DIR = pathlib.Path(__file__).resolve().parent.parent.parent
LOGGING_FILE = PERIODICA_DIR / "src" / "execution.log"

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
    def __init__(self, *, debug=False):
        self.debug = debug

    def info(self, message):
        from .terminal import animate_print, fore, GREEN
        logging.info(message)
        if self.debug:
            animate_print(fore("INFO: " + message, GREEN))

    def warn(self, message):
        from .terminal import animate_print, fore, YELLOW
        logging.warning(message)
        if self.debug:
            animate_print(fore("WARNING: " + message, YELLOW))

    def error(self, message):
        from .terminal import animate_print, fore, RED
        logging.error(message)
        if self.debug:
            animate_print(fore("ERROR: " + message, RED))

    def fatal(self, message):
        from .terminal import animate_print, fore, BLUE
        logging.fatal(message)
        if self.debug:
            animate_print(fore("FATAL: " + message, BLUE))

    def abort(self, message):
        self.error(message)
        time.sleep(1)
        self.fatal("Program terminated.")
        sys.exit(1)

log = Logger(debug=False)
default_config = {
    "use_superscripts": True,
    "truecolor": True,
    "isotope_format": "fullname-number",
    "animation": "none",
    "animation_delay": 0.0005
}

valid_formats = ["fullname-number", "symbol-number", "numbersymbol", "number-symbol"]
valid_animations = ["char", "line", "none"]

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
        elif key == "animation" and _config.get(key) not in valid_animations:
            _config[key] = default
        else:
            _config.setdefault(key, default)

    return _config

def save_config():
    global _config
    with open(PERIODICA_DIR / "src" / "config.json", "w", encoding="utf-8") as file:
        json.dump(_config or default_config, file, indent=4)

def get_response(url: str):
    from .terminal import animate_print
    try:
        import requests
    except ImportError:
        animate_print("Whoopsies, the requests module was not found in your environment! Please read the README.md file for more information.")
        log.abort("Couldn't proceed; the requests library was not found in the environment.")
    try:
        response = requests.get(url)
        response.raise_for_status()
        animate_print(f"HTTP status code: {response.status_code} (pass)")
        return response
    except requests.exceptions.ConnectionError:
        animate_print("Whoops! There was a network connection error. Please check your network connection, and try again later.")
        log.abort("Couldn't proceed; failed to connect to page.")
    except requests.exceptions.HTTPError:
        animate_print(f"Failed to download data! HTTP status code: {response.status_code}")
        log.abort(f"Failed to fetch data. Status code: {response.status_code}.")
