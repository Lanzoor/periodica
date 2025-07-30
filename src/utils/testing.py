import sys
from utils.terminal import BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, DEFAULT_COLOR
from utils.terminal import BRIGHT_BLACK, BRIGHT_RED, BRIGHT_GREEN, BRIGHT_YELLOW, BRIGHT_BLUE, BRIGHT_MAGENTA, BRIGHT_CYAN, BRIGHT_WHITE
from utils.terminal import fore, back, bold, italic, dim, underline, inverse_color, gradient, clear_screen, clear_line, animate_print

if __name__ == "__main__":
    print("Please refrain from running this script manually. Instead, please run the periodica.sh file with the --test flag.")
    sys.exit(0)

clear_screen()

colors = [
    BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE
]

bright_colors = [
    BRIGHT_BLACK, BRIGHT_RED, BRIGHT_GREEN, BRIGHT_YELLOW, BRIGHT_BLUE, BRIGHT_MAGENTA, BRIGHT_CYAN, BRIGHT_WHITE
]

fore_text = ""
for color in colors:
    fore_text += fore("text", color)

bright_fore_text = ""
for bright_color in bright_colors:
    bright_fore_text += fore("text", bright_color)

print("Fore colors:")
print("    " + fore_text)
print("    " + bright_fore_text)

back_text = ""
for color in colors:
    back_text += back("text", color)

bright_back_text = ""
for bright_color in bright_colors:
    bright_back_text += back("text", bright_color)

print("Background colors:")
print("    " + back_text)

for color in colors:
    print("    " + fore(back_text, color))

print("Truecolor and gradient testing:")
print(gradient("    This should be a rainbow. If not, please disable terminal_effects in config.", (255, 0, 0), (255, 0, 255)))

print("Styles:")
print(f"    Bold text: {bold("text")}")
print(f"    Italic text: {italic("text")} <- may behave the same as inverse_color")
print(f"    Dim text: {dim("text")} <- may not be widely supported")
print(f"    Underlined text: {underline("text")} <- also may not be widely supported, may be treated as bold")
print(f"    Inverse color: {inverse_color("This should be flipped colors")} and {inverse_color(fore("so should this", GREEN))}")
