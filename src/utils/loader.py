import json, os, logging

LOG_PATH = os.path.join(os.path.dirname(__file__), "../execution.log")

with open(LOG_PATH, 'w', encoding="utf-8"):
    pass

logging.basicConfig(
    filename=LOG_PATH,
    filemode='w',
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "../config.json")

default_config = {
    "use_superscripts": True,
    "truecolor": True,
    "isotope_format": "fullname-number",
    "animation": "none",
    "animation_delay": 0.001
}

valid_formats = ["fullname-number", "symbol-number", "numbersymbol"]
valid_animations = ["char", "line", "none"]

_config = None

def get_config():
    global _config
    if _config is not None:
        return _config

    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as file:
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
    with open(CONFIG_PATH, "w", encoding="utf-8") as file:
        json.dump(_config or default_config, file, indent=4)
