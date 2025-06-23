from .terminal import (
    bold, dim, italic, underline, crossout, blink,
    inverse_color, gradient, fore, animate_print,
    clear_screen, clear_line,
    BLACK, RED, GREEN, YELLOW, BLUE,
    MAGENTA, CYAN, WHITE, DEFAULT_COLOR,
)

from .config_loader import get_config, save_config, valid_formats, valid_animations, default_config

__all__ = [
    "bold", "dim", "italic", "underline", "crossout", "blink",
    "inverse_color", "gradient", "fore", "animate_print",
    "clear_screen", "clear_line",
    "BLACK", "RED", "GREEN", "YELLOW", "BLUE",
    "MAGENTA", "CYAN", "WHITE", "DEFAULT_COLOR",
    "get_config", "save_config", "valid_formats", "valid_animations", "default_config"
]
