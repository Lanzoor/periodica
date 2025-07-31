from utils.loader import get_config, logging
import re, sys, time, colorsys

config = get_config()
animation_type = config["animation_type"]
animation_delay = config["animation_delay"]
support_effects = config["terminal_effects"]

# Default supported terminal colors
BLACK = 0
RED = 1
GREEN = 2
YELLOW = 3
BLUE = 4
MAGENTA = 5
CYAN = 6
WHITE = 7
DEFAULT_COLOR = 9

BRIGHT_BLACK = 0 + 60
BRIGHT_RED = 1 + 60
BRIGHT_GREEN = 2 + 60
BRIGHT_YELLOW = 3 + 60
BRIGHT_BLUE = 4 + 60
BRIGHT_MAGENTA = 5 + 60
BRIGHT_CYAN = 6 + 60
BRIGHT_WHITE = 7 + 60

def fore(string, color: int | list[int] | tuple[int, int, int]) -> str:
    if isinstance(color, int):
        processed = str(string)
        if (color > 7 and color != 9 and color < 60) or (color > 67): raise Exception("Unsupported default terminal color.")
        try:
            return f"\033[{(30 + color)}m{processed}\033[39m"
        except ValueError:
            logging.warning(f"{color} was an invalid default terminal color. To the developers, please diagnose this issue.")
            return processed
    else:
        processed = str(string)
        red, green, blue = color
        return f"\033[38;2;{red};{green};{blue}m{processed}\033[39m"

def back(string, color: int | list[int] | tuple[int, int, int]) -> str:
    if isinstance(color, int):
        processed = str(string)
        if (color > 7 and color != 9 and color < 60) or (color > 67): raise Exception("Unsupported default terminal color.")
        try:
            return f"\033[{(40 + color)}m{processed}\033[49m"
        except ValueError:
            logging.warning(f"{color} was an invalid default terminal color. To the developers, please diagnose this issue.")
            return processed
    else:
        processed = str(string)
        red, green, blue = color
        return f"\033[48;2;{red};{green};{blue}m{processed}\033[49m"

def bold(string) -> str:
    return f"\033[1m{string}\033[22m"

def dim(string) -> str:
    if support_effects:
        return f"\033[2m{string}\033[22m"
    else:
        return string

def italic(string) -> str:
    if support_effects:
        return f"\033[3m{string}\033[23m"
    else:
        return bold(string)

def underline(string) -> str:
    if support_effects:
        return f"\033[4m{string}\033[24m"
    else:
        return bold(string)

def inverse_color(string) -> str:
    return f"\033[7m{string}\033[27m"

def gradient(message, start_rgb: list[int] | tuple[int, int, int], end_rgb: list[int] | tuple[int, int, int]):
    start_hue, start_lightness, start_saturation = colorsys.rgb_to_hls(
        start_rgb[0] / 255, start_rgb[1] / 255, start_rgb[2] / 255
    )
    end_hue, end_lightness, end_saturation = colorsys.rgb_to_hls(
        end_rgb[0] / 255, end_rgb[1] / 255, end_rgb[2] / 255
    )

    string_length = len(message)
    if string_length == 0:
        return ""

    result_characters = list(message)

    for index, character in enumerate(result_characters):
        interpolation_factor = index / (string_length - 1) if string_length > 1 else 0
        interpolated_hue = start_hue + (end_hue - start_hue) * interpolation_factor
        interpolated_lightness = start_lightness + (end_lightness - start_lightness) * interpolation_factor
        interpolated_saturation = start_saturation + (end_saturation - start_saturation) * interpolation_factor

        red, green, blue = [
            int(value * 255)
            for value in colorsys.hls_to_rgb(interpolated_hue, interpolated_lightness, interpolated_saturation)
        ]

        result_characters[index] = fore(character, (red, green, blue))
    return "".join(result_characters)

def clear_screen():
    if support_effects:
        print("\r\033[2J\033[H", end='', flush=True)

def clear_line():
    if support_effects:
        print("\r\033[2K", end='', flush=True)

def animate_print(message: str = "", delay: float = animation_delay, *, end: str = "\n"):
    global animation_type
    if animation_type == "char":
        ansi_escape = re.compile(r'(\x1b\[[0-9;]*m)')
        parts = ansi_escape.split(message)
        active_styles = ""
        for part in parts:
            if ansi_escape.fullmatch(part):
                active_styles = part
                sys.stdout.write(part)
                sys.stdout.flush()
            else:
                for char in part:
                    sys.stdout.write(f"{active_styles}{char}")
                    sys.stdout.flush()
                    time.sleep(delay)
    elif animation_type == "line":
        for line in message.splitlines():
            sys.stdout.write(line + "\n")
            sys.stdout.flush()
            time.sleep(delay)
    elif animation_type == "none":
        print(message, end="")

    print(end, end="")
