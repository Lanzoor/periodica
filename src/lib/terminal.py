from lib.loader import logging
import re, sys, time, colorsys

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

def fore(string, color: int | list[int] | tuple[int, int, int], *, disable: bool = False) -> str:
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

def back(string, color: int | list[int] | tuple[int, int, int], *, disable: bool = False) -> str:
    if not disable:
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
    return string

def bold(string, *, disable: bool = False) -> str:
    return f"\033[1m{string}\033[22m" if not disable else string

def dim(string, *, disable: bool = False) -> str:
    return f"\033[2m{string}\033[22m" if not disable else string

def italic(string, *, disable: bool = False) -> str:
    if not disable:
        return f"\033[3m{string}\033[23m"
    else:
        return string

def underline(string, *, disable: bool = False) -> str:
    if not disable:
        return f"\033[4m{string}\033[24m"
    else:
        return string

def inverse_color(string, *, disable: bool = False) -> str:
    return f"\033[7m{string}\033[27m" if not disable else string

def gradient(message, start_rgb: list[int] | tuple[int, int, int], end_rgb: list[int] | tuple[int, int, int], *, disable: bool = False):
    if not disable:
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
    else:
        return message
