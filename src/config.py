import json, time, sys, re

def fore(string, color: int | list[int] | tuple[int, int, int], *, bright: bool = False) -> str:
    if isinstance(color, int):
        processed = str(string)
        if color > 7 and color != 9: raise Exception("Unsupported default terminal color.")
        try:
            return f"\033[{(30 + color) if not bright else (90 + color)}m{processed}\033[39m"
        except ValueError:
            raise Exception("Unsupported default terminal color.")
    else:
        processed = str(string)
        r, g, b = color
        return f"\033[38;2;{r};{g};{b}m{processed}\033[39m"

def bold(string) -> str:
    return f"\033[1m{string}\033[22m"

default_options = {
    "use_superscripts": True,
    "truecolor": True,
    "isotope_format": "fullname-number",
    "animation": "none",
    "animation_delay": 0.001
}

valid_formats = ["fullname-number", "symbol-number", "numbersymbol"]
valid_animations = ["char", "line", "none"]

BLACK = 0
RED = 1
GREEN = 2
YELLOW = 3
BLUE = 4
MAGENTA = 5
CYAN = 6
WHITE = 7
DEFAULT_COLOR = 9

def clear_screen():
    print("\r\033[2J\033[H", end='', flush=True)

def clear_line():
    print("\r\033[2K", end='', flush=True)

try:
    with open('./config.json', 'r', encoding="utf-8") as file:
        config = json.load(file)
        print("The configuration file was found! Let's start editing it.")
except json.JSONDecodeError:
    with open('./config.json', 'w', encoding="utf-8") as file:
        config = default_options
        json.dump(default_options, file)
        print("Overwrited configuration file since it was malformed.")
except FileNotFoundError:
    with open('./config.json', 'w', encoding="utf-8") as file:
        config = default_options
        json.dump(default_options, file)
        print("Created a new configuration file, since it didn't exist.")

def save_config():
    global config
    with open('./config.json', 'w', encoding="utf-8") as file:
        json.dump(config, file, indent=4)

superscripts = config["use_superscripts"]
truecolor = config["truecolor"]
isotope_format = config["isotope_format"]
animation_type = config["animation"]
animation_delay = config["animation_delay"]

options_length = len(list(default_options.keys()))

for key, value in default_options.items():
    if key == "isotope_format":
        if config[key] not in valid_formats:
            config[key] = value
    elif key == "animation":
        if config[key] not in valid_animations:
            config[key] = value
    else:
        config.setdefault(key, value)

save_config()

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
        print(message)
    print(end, end="")

try:
    while True:
        superscripts = config["use_superscripts"]
        truecolor = config["truecolor"]
        isotope_format = config["isotope_format"]
        animation_type = config["animation"]
        animation_delay = config["animation_delay"]

        clear_screen()
        animate_print("Here are all avaliable options that you can change in your config file.\n")
        animate_print(f"1. Use Superscripts: Determines whether to use superscripts (Set to {bold(fore(superscripts, GREEN) if superscripts else fore(superscripts, RED))})")
        animate_print(f"2. Use Truecolor: Determines whether to use RGB-accurate coloring in terminal (Set to {bold(fore(truecolor, GREEN) if truecolor else fore(truecolor, RED))})")
        animate_print("3. Isotope Display Format: Determines how isotopes are formatted")
        animate_print(f"4. Print Animation: Determines the print animation (Set to {bold(animation_type.capitalize())})")
        animate_print(f"5. Animation Delay: Determines the delay between lines / characters based on animation type, does not work when animation is set to 'none' (Set to {bold(fore(animation_delay, CYAN))})\n")

        animate_print(f"To change a setting, please input the corresponding function name. To exit, please enter the {bold('q')} key.")
        user_input = input("> ").lower().strip()

        try:
            if user_input == "q":
                for i in range(3, 0, -1):
                    animate_print(f"Exiting program in {bold(i)}..", end="")
                    time.sleep(2)
                    clear_line()
                save_config()
                sys.exit(0)
            user_input = int(user_input)
        except ValueError:
            animate_print(fore(f"{user_input} is not a valid function number. Can you please try again?", RED))

            time.sleep(2)
            continue

        match user_input:
            case 1:
                config['use_superscripts'] = not config['use_superscripts']
                superscripts = config["use_superscripts"]
                animate_print(f"The setting 'Use Superscripts' was changed to {bold(fore(superscripts, GREEN) if superscripts else fore(superscripts, RED))}.")
                time.sleep(2)
            case 2:
                config['truecolor'] = not config['truecolor']
                truecolor = config["truecolor"]
                animate_print(f"The setting 'Use Truecolor' was changed to {bold(fore(truecolor, GREEN) if truecolor else fore(truecolor, RED))}.")
                time.sleep(2)
            case 3:
                while True:
                    clear_screen()
                    animate_print("You are about to change the isotope display format. Here are all valid options;\n")

                    animate_print(f"1. fullname-number (preview: {bold("Helium-8")})")
                    animate_print(f"2. symbol-number (preview: {bold("He-8")})")
                    animate_print(f"3. numbersymbol (preview: {bold("8He")})\n")

                    animate_print("To change to an option, please input the corresponding option name, or the option number.")
                    user_input = input("> ").lower().strip()

                    try:
                        user_input = int(user_input)
                        config['isotope_format'] = valid_formats[user_input - 1]
                        isotope_format = config["isotope_format"]
                        animate_print(f"Successfully changed option 'Isotope Format' to {bold(isotope_format)}.")
                        time.sleep(2)
                        break
                    except ValueError:
                        if user_input not in valid_formats:
                            animate_print(f"{user_input} is neither a valid option name nor a valid option number. Please try again.")
                            continue
                        config['isotope_format'] = user_input
                        isotope_format = config["isotope_format"]
                        animate_print(f"Successfully changed option 'Isotope Format' to {bold(isotope_format)}.")
                        time.sleep(2)
                        break
            case 4:
                while True:
                    clear_screen()
                    animate_print("You are about to change the animation type. Here are all valid options;\n")

                    animate_print("1. char (character-by-character animation)")
                    animate_print("2. line (line-by-line animation)")
                    animate_print("3. none (don't use any animations in output)")

                    animate_print("To change to an option, please input the corresponding option name, or the option number.")
                    user_input = input("> ").lower().strip()

                    try:
                        user_input = int(user_input)
                        config['animation'] = valid_animations[user_input - 1]
                        animation_type = config["animation"]
                        animate_print(f"Successfully changed option 'Animation Type' to {bold(animation_type)}.")
                        break
                    except ValueError:
                        if user_input not in valid_animations:
                            animate_print(f"{user_input} is neither a valid option name nor a valid option number. Please try again.")
                            continue
                        config['animation'] = user_input
                        animation_type = config["animation"]
                        animate_print(f"Successfully changed option 'Animation Type' to {bold(animation_type)}.")
                        break
            case 5:
                while True:
                    clear_screen()
                    animate_print("You are about to change the animation delay. Please input a float in seconds.")

                    user_input = input("> ").lower().strip()

                    try:
                        user_input = float(user_input)
                        if user_input > 0.25:
                            animate_print("Well, your delay was WAY LONG for our comprehension, and please do note it may take a very long time to display all the information.\nNonetheless, we value your configuration.")
                        config['animation_delay'] = user_input
                        animation_delay = config["animation_delay"]
                        animate_print(f"Successfully changed option 'Animation Delay' to {bold(animation_delay)}.")
                        time.sleep(2)
                        break
                    except ValueError:
                        if user_input not in valid_formats:
                            animate_print(f"{user_input} is not a valid float integer. Please try again.")
                            continue
                        config['animation_delay'] = user_input
                        animation_delay = config["animation_delay"]
                        animate_print(f"Successfully changed option 'Animation Delay' to {bold(animation_delay)}.")
                        time.sleep(2)
                        break
            case _:
                animate_print(fore(f"{user_input} is out of bounds. Can you please try again with a valid function number?", RED))

                time.sleep(2)
                continue
except KeyboardInterrupt:
    animate_print("\nYou have pressed ^C while editing the settings. Please do not do so. Your data has been saved anyways. Have a nice day!")
    save_config()
    time.sleep(2)
    sys.exit(0)
