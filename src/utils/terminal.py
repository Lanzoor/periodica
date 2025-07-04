from utils.loader import get_config, logging
import re, sys, time, colorsys

config = get_config()
animation_type = config["animation"]
animation_delay = config["animation_delay"]

BLACK = 0
RED = 1
GREEN = 2
YELLOW = 3
BLUE = 4
MAGENTA = 5
CYAN = 6
WHITE = 7
DEFAULT_COLOR = 9

B_BLACK = 0 + 60
B_RED = 1 + 60
B_GREEN = 2 + 60
B_YELLOW = 3 + 60
B_BLUE = 4 + 60
B_MAGENTA = 5 + 60
B_CYAN = 6 + 60

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
        r, g, b = color
        return f"\033[38;2;{r};{g};{b}m{processed}\033[39m"

def bold(string) -> str:
    return f"\033[1m{string}\033[22m"

def dim(string) -> str:
    return f"\033[2m{string}\033[22m"

def italic(string) -> str:
    return f"\033[3m{string}\033[23m"

def underline(string) -> str:
    return f"\033[4m{string}\033[24m"

def crossout(string) -> str:
    return f"\033[9m{string}\033[29m"

def blink(string) -> str:
    return f"\033[5m{string}\033[25m"

def inverse_color(string) -> str:
    return f"\033[7m{string}\033[27m"

def gradient(string, start_rgb: list[int] | tuple[int, int, int], end_rgb: list[int] | tuple[int, int, int]):
    processed = str(string)
    start_h, start_l, start_s = colorsys.rgb_to_hls(start_rgb[0] / 255, start_rgb[1] / 255, start_rgb[2] / 255)
    end_h, end_l, end_s = colorsys.rgb_to_hls(end_rgb[0] / 255, end_rgb[1] / 255, end_rgb[2] / 255)
    processed = [char for char in processed if char != " "]
    length = len(processed)
    res = list(processed)
    processed_index = 0
    for index, char in enumerate(res):
        if char == " ":
            continue
        interpolated_h = start_h + (end_h - start_h) * (processed_index / length)
        interpolated_l = start_l + (end_l - start_l) * (processed_index / length)
        interpolated_s = start_s + (end_s - start_s) * (processed_index / length)
        new_r, new_g, new_b = [int(element * 255) for element in colorsys.hls_to_rgb(interpolated_h, interpolated_l, interpolated_s)]
        res[index] = fore(char, (new_r, new_g, new_b))
        processed_index += 1
    return "".join(res)

def clear_screen():
    print("\r\033[2J\033[H", end='', flush=True)

def clear_line():
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
