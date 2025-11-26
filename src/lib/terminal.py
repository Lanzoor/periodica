from lib.loader import logging
import colorsys

# Default supported terminal colors
BRIGHT = 60
BLACK = 0
RED = 1
GREEN = 2
YELLOW = 3
BLUE = 4
MAGENTA = 5
CYAN = 6
WHITE = 7
DEFAULT_COLOR = 9

BRIGHT_BLACK = BRIGHT + BLACK
BRIGHT_RED = BRIGHT + RED
BRIGHT_GREEN = BRIGHT + GREEN
BRIGHT_YELLOW = BRIGHT + YELLOW
BRIGHT_BLUE = BRIGHT + BLUE
BRIGHT_MAGENTA = BRIGHT + MAGENTA
BRIGHT_CYAN = BRIGHT + CYAN
BRIGHT_WHITE = BRIGHT + WHITE

def fore(message: str, color: int | list[int] | tuple[int, int, int], *, disable: bool = False) -> str:
    if disable: return message

    if isinstance(color, int):
        if (color > 7 and color != 9 and color < 60) or (color > 67): raise Exception("Unsupported default terminal color.")
        try:
            return f"\033[{(30 + color)}m{message}\033[39m"
        except ValueError:
            logging.warning(f"{color} was an invalid default terminal color. To the developers, please diagnose this issue.")
            return message
    else:
        red, green, blue = color
        return f"\033[38;2;{red};{green};{blue}m{message}\033[39m"

def back(message: str, color: int | list[int] | tuple[int, int, int], *, disable: bool = False) -> str:
    if disable: return message

    if isinstance(color, int):
        if (color > 7 and color != 9 and color < 60) or (color > 67): raise Exception("Unsupported default terminal color.")
        try:
            return f"\033[{(40 + color)}m{message}\033[49m"
        except ValueError:
            logging.warning(f"{color} was an invalid default terminal color. To the developers, please diagnose this issue.")
        return message
    else:
        red, green, blue = color
        return f"\033[48;2;{red};{green};{blue}m{message}\033[49m"

def bold(string: str, *, disable: bool = False) -> str:
    if disable: return string
    return f"\033[1m{string}\033[22m"

def dim(string: str, *, disable: bool = False) -> str:
    if disable: return string
    return f"\033[2m{string}\033[22m"

def italic(string: str, *, disable: bool = False) -> str:
    if disable: return string
    return f"\033[3m{string}\033[23m"

def underline(string: str, *, disable: bool = False) -> str:
    if disable: return string
    return f"\033[4m{string}\033[24m"

def inverse(string: str, *, disable: bool = False) -> str:
    if disable: return string
    return f"\033[7m{string}\033[27m"

def gradient(string: str, start_rgb: list[int] | tuple[int, int, int], end_rgb: list[int] | tuple[int, int, int], *, disable: bool = False) -> str:
    if disable: return string

    start_hue, start_lightness, start_saturation = colorsys.rgb_to_hls(
        start_rgb[0] / 255, start_rgb[1] / 255, start_rgb[2] / 255
    )
    end_hue, end_lightness, end_saturation = colorsys.rgb_to_hls(
        end_rgb[0] / 255, end_rgb[1] / 255, end_rgb[2] / 255
    )

    string_length = len(string)
    if string_length == 0:
        return ""

    result_characters = list(string)

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
