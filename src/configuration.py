import time, sys, pathlib, subprocess
from utils.terminal import  RED, GREEN, CYAN, fore, bold, dim, clear_screen, clear_line
from utils.loader import get_config, save_config, valid_formats, valid_animation_types, default_config, Logger

if __name__ == "__main__":
    print("Please refrain from running this script manually. Instead, please run the periodica.sh file with the --init flag.")
    sys.exit(0)

PERIODICA_DIR = pathlib.Path(__file__).resolve().parent.parent
MAIN_FILE = PERIODICA_DIR / "src" / "main.py"
config = get_config()
constant_debugging = config["constant_debugging"]

if constant_debugging:
    logger = Logger(enable_debugging=True)
else:
    logger = Logger()


logger.info("Configuration program initialized.")

def fancy_abort():
    for i in range(3, 0, -1):
        print(f"Exiting program in {bold(i)}...", end="", flush=True)
        time.sleep(1)
        clear_line()
    sys.exit(0)

def create_fn_event(input: str, function_no: int, callable):
    if input == function_no:
        callable()
        return True
    return False

def toggle_superscript():
    global config, use_superscripts

    config['use_superscripts'] = not config['use_superscripts']
    use_superscripts = config["use_superscripts"]
    print(f"The setting 'Use Superscripts' was changed to {bold(fore(use_superscripts, GREEN) if use_superscripts else fore(use_superscripts, RED))}.")
    logger.info(f"Setting 'Use Superscripts' changed from {not use_superscripts} to {use_superscripts}.")
    time.sleep(1)

def toggle_truecolor():
    global config, support_truecolor

    config['truecolor'] = not config['truecolor']
    support_truecolor = config["truecolor"]
    print(f"The setting 'Use Truecolor' was changed to {bold(fore(support_truecolor, GREEN) if support_truecolor else fore(support_truecolor, RED))}.")
    logger.info(f"Setting 'Use Truecolor' changed from {not support_truecolor} to {support_truecolor}.")
    time.sleep(1)

def toggle_debugging():
    global config, constant_debugging

    config['constant_debugging'] = not config['constant_debugging']
    constant_debugging = config["constant_debugging"]
    print(f"The setting 'Debug Constantly' was changed to {bold(fore(constant_debugging, GREEN) if constant_debugging else fore(constant_debugging, RED))}.")
    logger.info(f"Setting 'Debug Constantly' changed from {not constant_debugging} to {constant_debugging}.")
    time.sleep(1)

def change_isotope_format():
    global config, isotope_format

    user_input = ""
    while user_input not in valid_formats:
        clear_screen()
        print("You are about to change the isotope display format. Here are all valid options;\n")

        print(f"1. fullname-number (preview: {bold("Helium-8")})")
        print(f"2. symbol-number (preview: {bold("He-8")})")
        print(f"3. numbersymbol (preview: {bold("8He")})")
        print(f"4. number-symbol (preview: {bold("8-He")})\n")

        print("To change to an option, please input the corresponding option name, or the option number.")
        user_input = input("> ").lower().strip()

        try:
            user_input = int(user_input)
            config['isotope_format'] = valid_formats[user_input - 1]
            isotope_format = config["isotope_format"]
            print(f"Successfully changed option 'Isotope Format' to {bold(isotope_format)}.")
            logger.info(f"Setting 'Isotope Format' changed to {isotope_format}.")
            time.sleep(1)
            break
        except ValueError:
            if user_input not in valid_formats:
                print(f"{user_input} is neither a valid option name nor a valid option number. Please try again.")
                logger.warn(f"{user_input} was neither a valid option name nor a valid option number.")
                continue
            config['isotope_format'] = user_input
            isotope_format = config["isotope_format"]
            print(f"Successfully changed option 'Isotope Format' to {bold(isotope_format)}.")
            logger.info(f"Setting 'Isotope Format' changed to {isotope_format}.")
            time.sleep(1)
            break

def change_animation_type():
    global config, animation_type

    user_input = ""
    while user_input not in valid_animation_types:
        clear_screen()
        print("You are about to change the animation type. Here are all valid options;\n")

        print("1. char (character-by-character animation)")
        print("2. line (line-by-line animation)")
        print("3. none (don't use any animations in output)")

        print("To change to an option, please input the corresponding option name, or the option number.")
        user_input = input("> ").lower().strip()

        try:
            user_input = int(user_input)
            config['animation'] = valid_animation_types[user_input - 1]
            animation_type = config["animation_type"]
            print(f"Successfully changed option 'Animation Type' to {bold(animation_type)}.")
            logger.info(f"Setting 'Animation Type' changed to {animation_type}.")
            break
        except ValueError:
            if user_input not in valid_animation_types:
                print(f"{user_input} is neither a valid option name nor a valid option number. Please try again.")
                logger.warn(f"{user_input} was neither a valid option name nor a valid option number.")
                continue
            config['animation'] = user_input
            animation_type = config["animation_type"]
            print(f"Successfully changed option 'Animation Type' to {bold(animation_type)}.")
            logger.info(f"Setting 'Animation Type' changed to {animation_type}.")
            break

def change_animation_delay():
    global config, animation_delay

    while True:
        clear_screen()
        print("You are about to change the animation delay. Please input a float in seconds.")

        user_input = input("> ").lower().strip()

        try:
            user_input = float(user_input)
            if user_input > 0.25:
                print("Well, your delay was WAY LONG for our comprehension, and please do note it may take a very long time to display all the information.\nNonetheless, we value your configuration.")
            config['animation_delay'] = user_input
            animation_delay = config["animation_delay"]
            print(f"Successfully changed option 'Animation Delay' to {bold(animation_delay)} seconds.")
            logger.info(f"Setting 'Animation Delay' changed to {animation_delay} seconds.")
            time.sleep(1)
            break
        except ValueError:
            print(f"{user_input} is not a valid float. Please try again.")
            logger.warn(f"{user_input} was not a valid float.")
            continue

def reset():
    global config

    clear_screen()
    print(fore(f"Are you sure? This action will reset all settings to the default settings. \n{bold("THIS ACTION IS IRREVERSIBLE.")} We highly recommend you to create backups before resetting the configuration.\n", RED))
    user_input = input(dim("Type '#' and press Enter to confirm the reset.") + "\n> ").lower().strip()
    if user_input == "#":
        config = default_config.copy()
        save_config()
        logger.info("User re-initialized the configuration. Restarting program...")
        print(bold("Your configuration has been reset. This program needs to restart in order to save the changes. Please run the script again."))
        fancy_abort()
    else:
        logger.info("User canceled configuration reset.")

try:
    while True:
        use_superscripts = config["use_superscripts"]
        support_truecolor = config["truecolor"]
        isotope_format = config["isotope_format"]
        animation_type = config["animation_type"]
        animation_delay = config["animation_delay"]
        constant_debugging = config["constant_debugging"]

        clear_screen()
        print("NOTE: This program intentionally does not respect your animation settings. Please understand.\n")
        print("Here are all available options that you can change in your config file.\n")
        print(f"1. Use Superscripts: Determines whether to use superscripts (Set to {bold(fore(use_superscripts, GREEN) if use_superscripts else fore(use_superscripts, RED))})")
        print(f"2. Use Truecolor: Determines whether to use RGB-accurate coloring in terminal (Set to {bold(fore(support_truecolor, GREEN) if support_truecolor else fore(support_truecolor, RED))})")
        print(f"3. Debug Constantly: Determines whether to log data constantly. Usually, you need the --debug flag to do it, but this constantly enables debug mode. (Set to {bold(fore(constant_debugging, GREEN) if constant_debugging else fore(constant_debugging, RED))})")
        print("4. Isotope Display Format: Determines how isotopes are formatted")
        print(f"5. Print Animation: Determines the print animation (Set to {bold(animation_type.capitalize())})")
        print(f"6. Animation Delay: Determines the delay between lines / characters based on animation type, does not work when animation is set to 'none' (Set to {bold(fore(animation_delay, CYAN))})")
        print(f"7. Reset Data: {bold("Overwrites all settings to the default settings.")}\n")

        print(f"To change a setting, please input the corresponding function name. To exit, please enter the {bold('q')} key.\nTo return to the main program, please enter the {bold('r')} key with optional arguments.")
        user_input = input("> ").lower().strip()

        try:
            if user_input in ["quit", "q", "abort", "exit"]:
                fancy_abort()
                save_config()
                logger.info("User quit the program. Aborting...")
                sys.exit(0)
            elif "r" in user_input.split(" ") or "return" in user_input.split(" ") or "ret" in user_input.split(" "):
                user_arguments = user_input.split(" ")
                user_arguments.remove("r")
                save_config()
                clear_screen()
                subprocess.run([sys.executable, str(MAIN_FILE), *user_arguments], check=True)
                sys.exit(0)

            user_input = int(user_input)
        except ValueError:
            print(fore(f"{user_input} is not a valid function number. Can you please try again?", RED))
            logger.warn(f"{user_input} was not a valid function number.")
            time.sleep(1)
            continue

        recognized_flag = (
            create_fn_event(user_input, 1, toggle_superscript) or
            create_fn_event(user_input, 2, toggle_truecolor) or
            create_fn_event(user_input, 3, toggle_debugging) or
            create_fn_event(user_input, 4, change_isotope_format) or
            create_fn_event(user_input, 5, change_animation_type) or
            create_fn_event(user_input, 6, change_animation_delay) or
            create_fn_event(user_input, 7, reset)
        )

        if not recognized_flag:
            print(fore(f"{user_input} is out of bounds. Can you please try again with a valid function number?", RED))

            logger.warn(f"{user_input} was an invalid function number.")
            time.sleep(1)
except KeyboardInterrupt:
    print("\nYou have pressed ^C while editing the settings. Please do not do so. Your data has been saved anyways. Have a nice day!")
    save_config()
    logger.info("User force quit the configuration program. Aborting...")
    sys.exit(0)
