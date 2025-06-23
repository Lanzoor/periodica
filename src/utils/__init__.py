from .terminal import (
    bold, dim, italic, underline, crossout, blink,
    inverse_color, gradient, fore, animate_print,
    clear_screen, clear_line,
    BLACK, RED, GREEN, YELLOW, BLUE,
    MAGENTA, CYAN, WHITE, DEFAULT_COLOR,
    B_BLACK, B_RED, B_GREEN, B_YELLOW, B_BLUE,
    B_MAGENTA, B_CYAN,
)

from .loader import get_config, save_config, valid_formats, valid_animations, default_config

__all__ = [
    "bold", "dim", "italic", "underline", "crossout", "blink",
    "inverse_color", "gradient", "fore", "animate_print",
    "clear_screen", "clear_line",
    "BLACK", "RED", "GREEN", "YELLOW", "BLUE",
    "MAGENTA", "CYAN", "WHITE", "DEFAULT_COLOR",
    "B_BLACK", "B_RED", "B_GREEN", "B_YELLOW", "B_BLUE",
    "B_MAGENTA", "B_CYAN",
    "get_config", "save_config", "valid_formats", "valid_animations", "default_config"
]
