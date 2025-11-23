import logging, time, sys, subprocess
from lib.directories import LOGGING_FILE, VENV_DIR, BUILD_SCRIPT

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
            print(bold(f"DEBUG: {message}"))

    def info(self, message):
        from .terminal import fore, GREEN
        logging.info(message)
        if self.enable_debugging:
            print(fore(f"INFO: {message}", GREEN))

    def warn(self, message):
        from .terminal import fore, YELLOW
        logging.warning(message)
        if self.enable_debugging:
            print(fore(f"WARNING: {message}", YELLOW))

    def error(self, message):
        from .terminal import fore, RED
        logging.error(message)
        if self.enable_debugging:
            print(fore(f"ERROR: {message}", RED))

    def fatal(self, message):
        from .terminal import fore, BLUE
        logging.fatal(message)
        if self.enable_debugging:
            print(fore(f"FATAL: {message}", BLUE))

    def abort(self, message):
        self.error(message)
        self.fatal("Program terminated.")
        sys.exit(0)

log = Logger(enable_debugging=False)

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
        print(f"Failed to download data! HTTP status code: {response.status_code}") # type: ignore
        log.abort(f"Failed to fetch data. Status code: {response.status_code}.") # type: ignore

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
