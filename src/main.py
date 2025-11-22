#!/usr/bin/env python3

try:
    import platform, sys, json, os, re, difflib, random, typing, textwrap, copy, functools, pprint
except ImportError:
    print("It seems like some of the standard libraries are missing. Please make sure you have the right version of the Python interpreter installed.")
    sys.exit(0)

import platform, sys, json, os, re, difflib, random, typing, textwrap, copy, functools

try:
    import lib, lib.loader, lib.terminal, lib.directories
except ImportError:
    print("The utils helper library or its scripts was not found. Please ensure all required files are present.")
    sys.exit(0)

from lib.loader import get_response, Logger, import_failsafe
from lib.terminal import RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, DEFAULT_COLOR, BRIGHT_BLACK, BRIGHT_GREEN, BRIGHT_RED
from lib.terminal import fore, back, inverse_color, bold, dim, italic, gradient
from lib.directories import ELEMENT_DATA_FILE, ISOTOPE_DATA_FILE, OUTPUT_FILE, UPDATE_SCRIPT
from pprint import pprint

# Just in case when the venv does not exist
import_failsafe()

# Flags for logic altering
EXPORT_ENABLED = False
DEBUG_MODE = False
ISOTOPE_LOGIC = False
VERBOSE = True

recognized_flag = False
data_malformed = False

# This is where elements and suggestions will go
full_element_data = {}
full_isotope_data = {}

current_element_data = None
current_element_suggestion = ""
current_isotope_data = None

logger = Logger(enable_debugging=DEBUG_MODE)

# Defining unicode symbols
def update_symbols(allow: bool = VERBOSE):
    global cm3, m3, mm2, superscript_pos, superscript_neg, superscript_zero, pm, emoji_chains, emoji_energy, rho, chi, full_block, up_arrow, down_arrow, sigma, double_line, single_line, PHASE_TYPE_SYMBOLS, CONDUCTIVITY_TYPE_SYMBOLS, emoji_exchange, emoji_speaker, emoji_radioactive

    cm3 = "cm³" if allow else "cm3"
    m3 = "m³" if allow else "m3"
    mm2 = "mm²" if allow else "mm2"

    emoji_chains = "⛓️" if allow else "d"
    emoji_energy = "⚡️" if allow else "E"
    emoji_exchange = "🔃" if allow else "<->"
    emoji_speaker = "📢" if allow else "->"
    emoji_radioactive = "☢️" if allow else "!"

    rho = "ρ" if allow else "p"
    chi = "χ" if allow else "x"
    full_block = "█" if allow else "-"
    up_arrow = "↑" if allow else "^"
    down_arrow = "↓" if allow else "_"
    sigma = "σ" if allow else "s"
    double_line = "═" if allow else "="
    single_line = "─" if allow else "-"
    superscript_pos = "⁺" if allow else "+"
    superscript_neg = "⁻" if allow else "-"
    superscript_zero = "⁰" if allow else "0"
    pm = "±" if allow else "+-"

    if allow:
        PHASE_TYPE_SYMBOLS = {
            "Solid": "🧊",
            "Gas": "💨",
            "Liquid": "💦"
        }

        CONDUCTIVITY_TYPE_SYMBOLS = {
            "Superconductor": "💨",
            "Semiconductor": "🔗",
            "Insulator": "🫧",
            "Conductor": "🔃",
            "Unsure": "❓"
        }
    else:
        PHASE_TYPE_SYMBOLS = None
        CONDUCTIVITY_TYPE_SYMBOLS = None

update_symbols()

# Defining custom colors (if terminal_effects is enabled)
def update_color_configs(allow: bool = VERBOSE):
    global VALENCE_ELECTRONS_COL, ELECTRONEG_COL, TURQUOISE, PINK, MELT_COL, BOIL_COL, ORANGE, INDIGO, NULL, EXCITED, PERIWINKLE, GOLD, ELEMENT_TYPE_COLORS, PHASE_TYPE_COLORS, CONDUCTIVITY_TYPE_COLORS, SUBSHELL_COLORS

    VALENCE_ELECTRONS_COL = (248, 255, 166) if allow else YELLOW
    ELECTRONEG_COL = (131, 122, 255) if allow else BLUE
    TURQUOISE = (109, 214, 237) if allow else CYAN
    PINK = (255, 133, 245) if allow else MAGENTA
    MELT_COL = (52, 110, 235) if allow else BLUE
    BOIL_COL = (189, 165, 117) if allow else YELLOW
    ORANGE = (245, 164, 66) if allow else YELLOW
    INDIGO = (94, 52, 235) if allow else BLUE
    NULL = (115, 255, 225) if allow else CYAN
    EXCITED = (185, 255, 128) if allow else BRIGHT_GREEN
    PERIWINKLE = (159, 115, 255) if allow else CYAN
    GOLD = (255, 209, 102) if allow else YELLOW

    ELEMENT_TYPE_COLORS = {
        "Reactive nonmetal": (130, 255, 151) if allow else BRIGHT_GREEN,
        "Noble gas": YELLOW,
        "Alkali metal": (215, 215, 215) if allow else BRIGHT_BLACK,
        "Alkali earth metal": ORANGE,
        "Metalloid": CYAN
    }

    PHASE_TYPE_COLORS = {
        "Solid": (156, 156, 156) if allow else BRIGHT_BLACK,
        "Gas": YELLOW,
        "Liquid": CYAN
    }

    CONDUCTIVITY_TYPE_COLORS = {
        "Superconductor": NULL,
        "Semiconductor": CYAN,
        "Insulator": RED,
        "Conductor": GOLD,
        "Unsure": EXCITED
    }

    SUBSHELL_COLORS = {
        's': RED,
        'p': GREEN,
        'd': CYAN,
        'f': MAGENTA
    }

update_color_configs()

# For ionization calculations
SUBSHELL_AZIMUTHALS = {
    's': 0,
    'p': 1,
    'd': 2,
    'f': 3
}

# Selecting random tips
def pick_tip(tips: list[str]) -> str:
    tips_copy = tips[:]
    tips_copy.append("")
    return random.choice(tips_copy)

normal_tips = [
    "(Tip: You can give this program argv to directly search an element from there. You can even give argv to the periodica.sh file too!)",
    "(Tip: Run this script with the --info flag to get information about flags.)",
    "(Tip: In an input field, you can input quit (as well as a few more keywords) to exit the interactive input session.)",
    "(Tip: There are shorthand aliases to common flags, run the script with the --info (or -i) flag to get information about them.)",
]

tip = pick_tip(normal_tips)

compare_tips = [
    "(Tip: You can give the arguments 'ascending', 'descending', and 'name' to change sort behavior.)",
    "(Tip: You can still input factors without underscores in the interactive text input field. Just not in arguments.)",
    "(Tip: If you accidentally give two or more sorting methods as input in argv, only the first one will be used.)"
]

compare_tip = pick_tip(compare_tips)

modifier_flags = {"--debug", "-d", "--raw", "-r"}

positionarg_req_flags = {
    "--export", "-x",
    "--compare", "-C",
    "--bond-type", "-B",
}

positionarg_nreq_flags = {
    "--info", "-i",
    "--random", "-R",
    "--version", "-v",
    "--update", "-u",
}

valid_flags = modifier_flags | positionarg_req_flags | positionarg_nreq_flags

def get_positional_args() -> list[str]:
    return [arg for arg in sys.argv[1:] if not arg.startswith("-")]

def get_flags() -> list[str]:
    return [arg for arg in sys.argv[1:] if arg.startswith("-")]

positional_arguments = [arg.strip() for arg in get_positional_args()]
flag_arguments = [arg.strip() for arg in get_flags()]

# Expand combined short flags
separated_flags: list[str] = []
for flag in flag_arguments:
    if flag.startswith("--"):
        separated_flags.append(flag)
    elif flag.startswith("-") and len(flag) > 2:
        for char in flag[1:]:
            separated_flags.append(f"-{char}")
    else:
        separated_flags.append(flag)

# Unit conversion functions
def celcius_to_kelvin(celsius):
	return round((celsius + 273.15), 5)

def celcius_to_fahrenheit(celsius):
	return round((celsius * 9 / 5) + 32, 5)

def format_temperature(variable):
    return f"{bold(variable)}°C ≈ {bold(celcius_to_fahrenheit(variable))}°F = {bold(celcius_to_kelvin(variable))}K"

def eV_to_kJpermol(eV):
    return round(eV * 96.485, 5)

def format_energy(variable):
    return f"{bold(variable)}eV ≈ {bold(eV_to_kJpermol(variable))}kJ/mol"

def print_header(title, double=False):
    dash = double_line if double else single_line
    dashes = dash * (TERMINAL_WIDTH - len(title) - 4)
    print(f"{dash * 2} {bold(title)} {dashes}")

def print_separator():
    print()
    print(single_line * TERMINAL_WIDTH)
    print()

def check_for_termination(user_input):
    if user_input in ["quit", "q", "abort", "exit", "terminate", "stop"]:
        print("Okay. Exiting...")
        logger.abort("User exited interactive input.")

def ordinal(number):
    if 10 <= number % 100 <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(number % 10, "th")
    return f"{number}{suffix}"

def parse_electron_configuration(subshells: list[str]) -> list[tuple[int, str, int]]:
    if not isinstance(subshells, list) or not all(isinstance(s, str) for s in subshells):
        logger.error(f"Expected list[str], got {type(subshells)}: {subshells}")
        return []
    config = []
    pattern = re.compile(r"(\d+)([spdf])(\d+)")
    for subshell in subshells:
        match = pattern.fullmatch(subshell)
        if match:
            quantum_no, azimuthal_no, count = match.groups()
            config.append((int(quantum_no), azimuthal_no, int(count)))
        else:
            logger.warn(f"Malformed subshell detected: {subshell}")
    return config

def calculate_shielding_constant(subshell_list: list[str], target_subshell: str) -> float:
    if not isinstance(subshell_list, list) or not all(isinstance(s, str) for s in subshell_list):
        logger.error(f"Expected list[str], got {type(subshell_list)}: {subshell_list}")
        return 0.0
    if not isinstance(target_subshell, str) or len(target_subshell) < 2:
        logger.error(f"Invalid target subshell: {target_subshell}")
        return 0.0

    try:
        target_principal_quantum_number, target_subshell_type = int(target_subshell[0]), target_subshell[1]
        target_azimuthal_quantum_number = {"s": 0, "p": 1, "d": 2, "f": 3}[target_subshell_type]
    except (IndexError, KeyError, ValueError):
        logger.warn(f"Invalid target subshell format: {target_subshell}")
        return 0.0

    configuration = parse_electron_configuration(subshell_list)
    if not configuration:
        logger.warn(f"No valid configuration for subshell list: {subshell_list}")
        return 0.0

    shielding_constant = 0.0
    for principal_quantum_number, subshell_type, electron_count in configuration:
        if principal_quantum_number == target_principal_quantum_number:
            contribution = 0.30 if subshell_type == "s" and principal_quantum_number == 1 else 0.35
            if subshell_type == target_subshell_type:
                shielding_constant += contribution * (electron_count - 1)
            else:
                shielding_constant += contribution * electron_count
        elif principal_quantum_number == target_principal_quantum_number - 1:
            shielding_constant += 0.85 * electron_count if target_azimuthal_quantum_number in (0, 1) else 1.00 * electron_count
        elif principal_quantum_number < target_principal_quantum_number - 1:
            shielding_constant += 1.00 * electron_count

    return shielding_constant

def calculate_ionization_series(subshells: list[str], atomic_number: int, ionization_energy: float | None) -> str:
    lines = []
    config = parse_electron_configuration(subshells)
    if not config:
        return fore("No valid subshell data for ionization series.", YELLOW)

    RYDBERG_CONSTANT = 13.6
    uncertainty = ""

    current_config = copy.deepcopy(config)
    for index in range(atomic_number):
        last_filled = None
        last_idx = None
        for idx in range(len(current_config) - 1, -1, -1):
            quantum_no, azimuthal_no, count = current_config[idx]
            if count > 0:
                last_filled = (quantum_no, azimuthal_no)
                last_idx = idx
                break

        if last_filled is None:
            break

        subshell_str = f"{last_filled[0]}{last_filled[1]}"
        quantum_target = last_filled[0]
        current_subshells = [f"{q}{a}{c}" for q, a, c in current_config if c > 0]
        shielding_constant = calculate_shielding_constant(current_subshells, subshell_str)
        Z_eff = atomic_number - shielding_constant

        if index == 0 and ionization_energy is not None:
            current_IE = ionization_energy
        else:
            current_IE = RYDBERG_CONSTANT * (Z_eff ** 2) / (quantum_target ** 2)

        if index == 0:
            uncertainty = "eV"
        elif index == 1:
            # The first breakdown always has a lot of inaccuracy
            uncertainty = f"{pm}75eV"
        elif index < atomic_number // 2:
            # Then it settles in the next half
            uncertainty = f"{pm}50eV"
        elif index > atomic_number // 2:
            # The last half and especially the last one is actually pretty accurate
            current_IE = RYDBERG_CONSTANT * (Z_eff ** 2) / (quantum_target ** 2)
            uncertainty = f"{pm}25eV"

        formatted_subshell = f"{subshell_str}1"
        formatted_subshell = formatted_subshell[:-1] + convert_superscripts(formatted_subshell[-1]) if VERBOSE else formatted_subshell

        # Appending to the output
        lines.append(
            f"  - {bold(ordinal(index + 1))} Ionization:\n"
            f"    {fore('Removed Subshell', RED)}: {formatted_subshell}\n"
            f"    {sigma} - {fore('Shielding Constant', PERIWINKLE)}: {shielding_constant:.2f}\n"
            f"    Z_eff - {fore('Effective Nuclear Charge', GOLD)}: {Z_eff:.2f}\n"
            f"    {fore('Ionization Energy', PINK)}: {bold(round(current_IE, 3))}{uncertainty}\n"
        )

        if last_idx is not None:
            quantum_no, azimuthal_no, count = current_config[last_idx]
            current_config[last_idx] = (quantum_no, azimuthal_no, count - 1)

    return "\n".join(lines)

def convert_superscripts(text: str) -> str:
    superscript_map = {
        "0": "⁰", "1": "¹", "2": "²", "3": "³", "4": "⁴",
        "5": "⁵", "6": "⁶", "7": "⁷", "8": "⁸", "9": "⁹",
        "+": "⁺", "-": "⁻"
    }
    return "".join(superscript_map.get(char, char) for char in text)

def conjunction_join(entries: list) -> str:
    if not entries:
        return ""
    if len(entries) == 1:
        return entries[0]
    if len(entries) == 2:
        return f"{entries[0]} and {entries[1]}"
    return f"{', '.join(entries[:-1])}, and {entries[-1]}"

def create_flag_event(*flags: str, callable):
    for flag in separated_flags:
        if flag in flags:
            logger.debug(f"Flag matched: {flag}, calling {callable.__name__}")
            callable()
            return True
    return False

# Below are functions that get triggered by create_flag_event when flags are given
def get_information():
    logger.info("User gave --info flag; redirecting to information logic.")
    print(program_information)
    sys.exit(0)

def check_for_updates():
    logger.info("User gave --update flag; redirecting to update logic.")
    if UPDATE_SCRIPT.is_file():
        from update import update_main
        update_main()
        sys.exit(0)
    else:
        print(fore("Looks like the update script is missing. Please check for any missing files.", RED))
        logger.abort("Failed to find the update script.")

def export_element():
    global EXPORT_ENABLED, positional_arguments

    logger.info("User gave --export flag; redirecting to export logic.")
    EXPORT_ENABLED = True

    user_input = positional_arguments[0] if positional_arguments else None

    element = None

    if user_input is not None:
        element, suggestion = process_isotope_input(user_input)
        if element is None and not suggestion:
            print(fore("Could not find that element or isotope. Please enter one manually.", RED))
        elif element is None:
            print(fore(f"Could not find that element or isotope. Did you mean {suggestion}?", YELLOW))

    if element is None:
        print(f"Search for an element {italic('to export')} by name, symbol, or atomic number.")
        while element is None:
            user_input = input("> ").strip()

            check_for_termination(user_input)

            element, suggestion = process_isotope_input(user_input)
            if element is None and not suggestion:
                print(fore("Could not find that element or isotope. Please enter one manually.", RED))
            elif element is None:
                print(fore(f"Could not find that element or isotope. Did you mean {suggestion}?", YELLOW))


    is_isotope = "info" in element and "symbol" in element

    if is_isotope:
        name = element["isotope"]
    else:
        name = element["general"]["fullname"].capitalize()

    print(f"Saving data of {bold(name)} to {OUTPUT_FILE}...")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        if is_isotope:
            json.dump(
                {
                    "symbol": element["symbol"].capitalize(),
                    "fullname": element["fullname"].capitalize(),
                    "isotope_name": element["isotope"],
                    "data": element["info"],
                },
                file,
                indent=4,
                ensure_ascii=False
            )
        else:
            json.dump(
                {
                    **element,
                    "isotopes": full_isotope_data.get(element["general"]["fullname"], {}),
                },
                file,
                indent=4,
                ensure_ascii=False
            )

    print(f"Successfully saved to {OUTPUT_FILE}.")
    sys.exit(0)

def compare_by_factor():
    global full_element_data, positional_arguments, compare_tip, valid_sorting_methods
    logger.info("User gave --compare flag; redirecting to another logic.")

    factors = [
        "protons",
        "electrons",
        "neutrons",
        "mass_number",
        "up_quarks",
        "down_quarks",
        "isotopes",
        "melting_point",
        "boiling_point",
        "atomic_mass",
        "electronegativity",
        "electron_affinity",
        "ionization_energy",
        "calculated_radius",
        "empirical_radius",
        "covalent_radius",
        "van_der_waals_radius",
        "brinell_hardness",
        "mohs_hardness",
        "vickers_hardness",
        "bulk_modulus",
        "young_modulus",
        "shear_modulus",
        "poissons_ratio",
        "stp_density",
        "liquid_density",
        "sound_transmission_speed"
    ]

    valid_sorting_methods = [
        "ascending",
        "descending",
        "name"
    ]
    determiner = ""
    sorting_method = "ascending"

    for index, argument in enumerate(positional_arguments):
        if argument in valid_sorting_methods:
            sorting_method = argument
            print(f"Using the sorting method {bold(argument)} for sorting...")
            logger.info(f"Using {argument} sorting for sorting.")
            del positional_arguments[index]
            break

    factor_candidate = positional_arguments[0] if positional_arguments else None

    if factor_candidate and factor_candidate not in factors:
        suggestion = difflib.get_close_matches(factor_candidate, factors, n=1, cutoff=0.6)
        if suggestion:
            print(fore(f"Not a valid factor. Did you mean \"{bold(suggestion[0])}\"?", YELLOW))
            logger.warn(f"No direct match found for '{factor_candidate}'. Found a close match; '{suggestion[0]}'?")
            factor_candidate = None
        else:
            print(fore("Not a valid factor. Please provide one manually.", RED))
            logger.warn(f"No direct match found for '{factor_candidate}'.")
            factor_candidate = None

    def get_key_by_input(element_data: dict[str, dict], isotope_data: dict[str, dict], factor: str):
        nonlocal determiner
        result = None
        try:
            match factor:
                case "protons":
                    result = element_data["nuclear"]["protons"]
                case "electrons":
                    result = element_data["nuclear"]["electrons"]
                case "neutrons":
                    result = element_data["nuclear"]["neutrons"]
                case "mass_number":
                    result = element_data["nuclear"]["protons"] + element_data["nuclear"]["neutrons"]
                case "up_quarks":
                    result = (element_data["nuclear"]["protons"] * 2) + element_data["nuclear"]["neutrons"]
                case "down_quarks":
                    result = element_data["nuclear"]["protons"] + (element_data["nuclear"]["neutrons"] * 2)
                case "isotopes":
                    result = len(list(isotope_data.keys()))
                case "melting_point":
                    determiner = "°C"
                    result = element_data["physical"]["melt"]
                case "boiling_point":
                    determiner = "°C"
                    result = element_data["physical"]["boil"]
                case "atomic_mass":
                    determiner = "g/mol"
                    result = element_data["physical"]["atomic_mass"]
                case "electronegativity":
                    result = element_data["electronic"]["electronegativity"]
                case "electron_affinity":
                    determiner = "eV"
                    result = element_data["electronic"]["electronegativity"]
                case "ionization_energy":
                    determiner = "eV"
                    result = element_data["electronic"]["ionization_energy"]
                case "calculated_radius" | "empirical_radius" | "covalent_radius" | "van_der_waals_radius":
                    determiner = "pm"
                    result = element_data["measurements"]["radius"][factor.replace("_radius", "")]
                case "brinell_hardness" | "mohs_hardness" | "vickers_hardness":
                    determiner = f"kgf/{mm2}" if determiner != "mohs_hardness" else ""
                    result = element_data["measurements"]["hardness"][factor.replace("_hardness", "")]
                case "bulk_modulus" | "young_modulus" | "shear_modulus":
                    determiner = "GPa"
                    result = element_data["measurements"]["moduli"][factor.replace("_modulus", "")]
                case "poissons_ratio":
                    result = element_data["measurements"]["moduli"]["poissons_ratio"]
                case "stp_density":
                    determiner = f"kg/{m3}"
                    result = element_data["measurements"]["density"]["STP"]
                case "liquid_density":
                    determiner = f"kg/{m3}"
                    result = element_data["measurements"]["density"]["liquid"]
                case "sound_transmission_speed":
                    determiner = "m/s"
                    result = element_data["measurements"]["sound_transmission_speed"]
        except (KeyError, ValueError) as error:
            logger.warn(f"Missing or invalid {factor} for {element_data['general']['fullname']}: {error}")
            return None

        try:
            return float(result) if result is not None else None
        except (ValueError, TypeError) as error:
            logger.warn(f"Couldn't convert data {result} from anything else to float: {error}")
            return None

    compare_tip = "\n" + compare_tip if compare_tip else ""

    formatted_factors = ', '.join(map(lambda element: bold(element), factors))
    formatted_factors = "\n" + "\n\n".join(
        textwrap.fill(paragraph.strip(), width=round(TERMINAL_WIDTH * 1.25), initial_indent="    ", subsequent_indent="")
        for paragraph in formatted_factors.strip().split("\n\n")
    ) + "\n"

    if factor_candidate not in factors:
        print(f"Please enter a factor to compare all the elements with. The valid factors are:\n  {formatted_factors}{dim(compare_tip)}")

    while True:
        if factor_candidate and factor_candidate in factors:
            factor = factor_candidate
            logger.info(f"Found a direct factor match from user input; {factor}")
            break

        if factor_candidate:
            suggestion = difflib.get_close_matches(factor_candidate, factors, n=1, cutoff=0.6)
            if suggestion:
                print(fore(f"Not a valid factor. Did you mean \"{bold(suggestion[0])}\"?", YELLOW))
                logger.warn(f"No direct match found for '{factor_candidate}'. Found a close match; '{suggestion[0]}'?")
            else:
                print(fore("Not a valid factor. Please try again.", RED))
                logger.warn(f"No direct match found for '{factor_candidate}'.")

        factor_candidate = "_".join(input("> ").strip().lower().split(" "))
        check_for_termination(factor_candidate)

    print(f"\nComparing all elements by factor {bold(factor)} in a(n) {bold(sorting_method)} order... {dim('(Please note that some elements may be missing, and the data is trimmed up to 4 digits of float numbers.)')}\n")
    logger.info(f"Comparing all elements by factor {factor}...")

    result: dict[str, float | int | None] = {}

    for element_name, element_value in full_element_data.items():
        isotope_value = full_isotope_data.get(element_name, {})
        result[element_name] = get_key_by_input(element_value, isotope_value, factor)

    valid_results = [(name, value) for name, value in result.items() if value is not None]
    if not valid_results:
        print(fore(f"No valid data for {factor}", RED))
        logger.error(f"No elements have valid {factor} data")
        sys.exit(0)

    match sorting_method:
        case "ascending" | "descending":
            sorted_results = sorted(result.items(), key=lambda item: (item[1] is None, item[1]))
            if sorting_method == "descending":
                sorted_results.reverse()
        case "name":
            sorted_results = result.items()
        case _:
            logger.warn(f"Invalid sorting method {sorting_method}. Please pay attention.")
            sorted_results = sorted(result.items(), key=lambda item: (item[1] is None, item[1]))

    max_value = max(value for _, value in valid_results) or 1
    none_counter = 0
    none_list = []

    for name, value in sorted_results:
        if value is not None:
            padding = 30 + len(determiner)
            bar_space = max(TERMINAL_WIDTH - padding, 10)
            bar_length = int((value / max_value) * bar_space)
            bar = fore(full_block * bar_length, CYAN)
            print(f"{name:<12} {str(round(value, 4)) + determiner:<12} [{bar}]")
        elif value is None:
            none_counter += 1
            none_list.append(name)
            print(f"{name:<12} {fore("None", NULL) + " " * 8} []")

    # Calculate stats
    valid_values = [value for _, value in valid_results]
    average = sum(valid_values) / len(valid_values) if valid_values else 0
    highest_pair = max(valid_results, key=lambda item: item[1])
    lowest_pair = min(valid_results, key=lambda item: item[1])
    formatted_nones = ', '.join(map(lambda element: bold(element), none_list))

    print()
    print(f"Average - {bold(round(average, 4))}{determiner}")
    print(f"Element with the highest {factor} is {bold(highest_pair[0])}, with {bold(highest_pair[1])}{determiner}.")
    print(f"Element with the lowest {factor} is {bold(lowest_pair[0])}, with {bold(lowest_pair[1])}{determiner}.")

    if none_counter > 0:
        print(fore(f"{none_counter} element(s) do not have a value in {bold(factor)}, and they are;\n  {formatted_nones}", NULL))
    sys.exit(0)

def compare_bond_type():
    global full_element_data, positional_arguments
    logger.info("User gave --bond-type flag; redirecting to bond type logic.")

    primary_element = None
    secondary_element = None

    if len(positional_arguments) >= 2:
        primary_element, _ = find_element(positional_arguments[0])
        secondary_element, _ = find_element(positional_arguments[1])

        if primary_element is None or secondary_element is None:
            print(fore("One or both elements could not be resolved from the arguments. Please provide them manually.", YELLOW))
            primary_element = None
            secondary_element = None
        else:
            logger.info(f"Resolved both elements from CLI args: {positional_arguments[0]}, {positional_arguments[1]}")

    if primary_element is None:
        print(f"Search for the primary element {italic('to compare the bond type')} with by name, symbol, or atomic number.")
        while True:
            user_input = input("> ").strip().lower()
            logger.info(f"Primary input: \"{user_input}\"")
            check_for_termination(user_input)

            primary_element, suggestion = find_element(user_input)
            if primary_element:
                break
            if suggestion:
                print(fore(f"Not a valid element. Did you mean \"{bold(suggestion)}\"?", YELLOW))
            else:
                print(fore(f"Not a valid element.", RED))

    primary_element_name = primary_element["general"]["fullname"]

    if secondary_element is None:
        print(f"Now, please enter the secondary element {italic('to compare the bond type')} with {bold(primary_element_name)}.")
        while True:
            user_input = input("> ").strip().lower()
            logger.info(f"Secondary input: \"{user_input}\"")
            check_for_termination(user_input)

            secondary_element, suggestion = find_element(user_input)
            if secondary_element:
                break
            if suggestion:
                print(fore(f"Not a valid element. Did you mean \"{bold(suggestion)}\"?", YELLOW))
            else:
                print(fore(f"Not a valid element.", RED))

    secondary_element_name = secondary_element["general"]["fullname"]
    primary_en = primary_element["electronic"]["electronegativity"]
    secondary_en = secondary_element["electronic"]["electronegativity"]

    if primary_en is None or secondary_en is None:
        print(fore("Failed to fetch bond type; one or both elements lack electronegativity values (likely inert).", YELLOW))
        sys.exit(0)

    diff = abs(primary_en - secondary_en)
    if diff < 0.4:
        bond_type_str = fore("Nonpolar Covalent", BLUE) + " -"
    elif diff < 1.7:
        bond_type_str = fore("Polar Covalent", YELLOW) + (" δ" if VERBOSE else " d")
    else:
        bond_type_str = fore("Ionic", RED) + (" →" if VERBOSE else " >")

    print()
    print(f"Primary element ({primary_element_name})'s electronegativity: {bold(primary_en)}")
    print(f"Secondary element ({secondary_element_name})'s electronegativity: {bold(secondary_en)}")
    print(f"Difference: {primary_en} - {secondary_en} = {bold(f'{diff:.3f}')}")
    print(f"Bond type: {bond_type_str} (According to Pauling's Electronegativity Method)")
    print()
    sys.exit(0)

def select_random_element():
    global current_element_data
    print("Picking a random element for you...")
    logger.info("Picking a random element...")

    current_element_data = random.choice(list(full_element_data.values()))
    print(f"I pick {bold(current_element_data["general"]["fullname"])} for you!")
    logger.info(f"Picked {current_element_data["general"]["fullname"]} as a random element.")

def enable_debugging():
    global DEBUG_MODE, logger
    DEBUG_MODE = True
    print(gradient("Debug mode enabled. Have fun...", ELECTRONEG_COL, NULL) if VERBOSE else fore("Debug mode enabled. Have fun...", BLUE)) # type: ignore
    logger = Logger(enable_debugging=DEBUG_MODE)
    logger.info("Enabled debug mode.")
    if flag_arguments:
        logger.info(f"Given flags: {", ".join(flag_arguments)}")

    if positional_arguments:
        logger.info(f"Other positional arguments given: {", ".join(positional_arguments)}")

def enable_raw_output():
    global VERBOSE, print, fore, back, bold, dim, italic, inverse_color, gradient
    VERBOSE = False
    logger.info("Enabled raw output mode.")

    funclist = ['fore', 'back', 'bold', 'dim', 'italic', 'inverse_color', 'gradient']
    for name in funclist:
        globals()[name] = functools.partial(globals()[name], disable=True)

    update_symbols(False)
    update_color_configs(False)

def fetch_version():
    global PYPROJECT_FILE
    from update import fetch_toml

    logger.info("User gave --version flag; showing version information.")

    local_version = fetch_toml()

    print(f"Version: {local_version}")
    print(f"Python Interpreter: {".".join(platform.python_version_tuple())}")

    sys.exit(0)

# Extract symbol and number from an isotope
def extract_isotope_factors(user_input: str) -> typing.Tuple[str | None, str | None]:
    match = re.match(r"^(\d+)([A-Za-z]+)$", user_input)
    if match:
        return match.group(2), match.group(1)

    match = re.match(r"^([A-Za-z]+)[\s\-]*(\d+)$", user_input)
    if match:
        return match.group(1), match.group(2)

    return None, None

def print_isotope(norm_iso, info, fullname):
    global animation_delay

    match = re.match(r"^(\d+)\s*([A-Za-z]+)$", norm_iso)
    display_name = format_isotope(norm_iso, fullname) if match else norm_iso

    symbol, number = extract_isotope_factors(norm_iso)
    superscript_name = convert_superscripts(number) + symbol

    alt_name_display = ", " + info['name'] if 'name' in info else ""
    name_display = f"({superscript_name}{italic(alt_name_display)})"
    print(f"  - {bold(display_name)} {name_display}:")

    protons = info['protons']
    neutrons = info['neutrons']
    print(f"      p{superscript_pos}, e{superscript_neg} - {fore('Protons', RED)} and {fore('Electrons', YELLOW)}: {bold(protons)}")
    print(f"      n{superscript_zero} - {fore('Neutrons', BLUE)}: {bold(neutrons)}")

    up_quarks = protons * 2 + neutrons
    down_quarks = protons + neutrons * 2
    print(f"      u - {fore('Up Quarks', GREEN)}: ({fore(protons, RED)} * 2) + {fore(neutrons, BLUE)} = {bold(up_quarks)}")
    print(f"      d - {fore('Down Quarks', CYAN)}: {fore(protons, RED)} + ({fore(neutrons, BLUE)} * 2) = {bold(down_quarks)}")

    half_life = info.get('half_life')
    print(f"      t1/2 - {fore("Half Life", PERIWINKLE)}: {bold(half_life) if half_life else fore('Stable', NULL)}")
    print(f"      u - {fore("Isotope Weight", BRIGHT_RED)}: {bold(info['isotope_weight'])}g/mol")

    def show_decay(decays, indent=12):
        padding = " " * indent

        verified = [decay for decay in decays if "chance" in decay]
        unverified = [decay for decay in decays if "chance" not in decay]

        verified.sort(key=lambda decay: decay["chance"], reverse=True)

        for branch in verified + unverified:
            mode = branch.get("mode", "???")
            if mode.endswith("?"):
                mode = fore(mode, RED)
            if "chance" in branch:
                chance = f"({branch['chance']}%)" if branch["chance"] != 100 else ""
            else:
                chance = ""
            products = branch.get("product", [])
            if not isinstance(products, list):
                products = [str(products)]
            out = ", ".join(bold(format_isotope(product, fullname)) for product in products)
            arrow = "->" if products else ""

            print(f"{padding}{bold(display_name)} -> {bold(mode)} {arrow} {out} {chance}")

    if isinstance(info.get("decay"), list):
        print(f"      {emoji_chains} - {fore("Possible Decays", GOLD)}:")
        show_decay(info["decay"])

    if isinstance(info.get("metastable"), dict):
        print(f"      m - {fore("Metastable Isotopes", EXCITED)}:")
        for state, data in info["metastable"].items():
            display_meta = format_isotope(norm_iso, fullname, metastable=state)
            print(f"        {bold(display_meta)}:")
            if "half_life" in data:
                print(f"          t1/2 - {fore("Half Life", PERIWINKLE)}: {bold(data['half_life'])}")
            print(f"          {emoji_energy} - {fore("Excitation Energy", EXCITED)}: {bold(data['energy'])}keV")
            if "decay" in data:
                print(f"          {emoji_chains} - {fore("Possible Decays", GOLD)}:")
                show_decay(data["decay"], indent=14)

# Formats an isotope respecting the isotope format
def format_isotope(norm_iso, fullname, *, metastable = ""):
    global isotope_format

    match = re.match(r"^(\d+)\s*([A-Za-z]+)$", norm_iso)
    if not match:
        return norm_iso
    else:
        number, symbol = match.groups()
        symbol = symbol.capitalize()
        return f"{fullname.capitalize()}-{number}{metastable}"

def recognize_isotope(element_identifier, mass_number, search_query):
    def use_isotope(isotopes, element_symbol, element_name, mass_number, search_query) -> dict | bool:
        global ISOTOPE_LOGIC

        normalized_mass_symbol = f"{mass_number}{element_symbol}"
        normalized_symbol_mass = f"{element_symbol}{mass_number}"

        for isotope, isotope_info in isotopes.items():
            normalized_isotope = normalize_isotope(isotope).lower()

            if (normalized_isotope in [normalized_mass_symbol, normalized_symbol_mass, search_query]):
                logger.info(f"Found isotope match: {isotope} ({mass_number}{element_symbol}) in {element_name}")
                if EXPORT_ENABLED:
                    return {
                        "isotope": isotope,
                        "symbol": element_symbol,
                        "fullname": element_name,
                        "info": isotope_info
                    }
                ISOTOPE_LOGIC = True
                print_separator()
                print_isotope(isotope, isotope_info, element_name)
                print_separator()
                return True

        print(fore(f"No isotope match found for mass number {mass_number} in element {element_name}. Please provide one manually.", YELLOW))
        logger.warn(f"No isotope match found for mass number {mass_number} in element {element_name}")
        return False

    element_identifier = element_identifier.lower()
    search_query = search_query.lower()
    logger.info(f"Searching for isotope: {element_identifier}, mass number: {mass_number}, query: {search_query}")

    for element_data in full_element_data.values():
        element_symbol = element_data["general"]["symbol"].lower()
        element_name = element_data["general"]["fullname"].lower()

        if element_identifier not in (element_symbol, element_name):
            continue

        logger.info(f"Element match found for '{element_identifier}': {element_name} ({element_symbol})")

        isotope_data = full_isotope_data.get(element_name.capitalize(), {})

        if not isotope_data:
            continue

        return use_isotope(
            isotope_data,
            element_symbol,
            element_name,
            mass_number,
            search_query
        )

    logger.warn(f"No element found for symbol or name: {element_identifier}")
    return False

def normalize_isotope(isotope):
    match = re.match(r"^(.*?)(?:\s*-\s*.*)?$", isotope)
    normalized = match.group(1) if match else isotope
    return normalized

def find_element(candidate) -> typing.Tuple[dict | None, str | None]:
    logger.info(f"Searching for element match: {candidate}")
    candidate = candidate.lower()
    possible_names = []

    for _, element_candidate_data in enumerate(full_element_data.values()):
        name = element_candidate_data["general"]["fullname"].lower()
        symbol = element_candidate_data["general"]["symbol"].lower()
        identifiers = element_candidate_data["general"]["identifiers"]

        possible_names.extend([name, symbol])

        if candidate in identifiers:
            logger.info(f"Exact match found: {name} ({symbol})")
            return element_candidate_data, None

    suggestion = difflib.get_close_matches(candidate, possible_names, n=1, cutoff=0.6)
    if suggestion:
        logger.warn(f"No direct match found for '{candidate}'. Found a close match; '{suggestion[0]}'?")
        return None, suggestion[0]

    logger.warn(f"No match or suggestion found for input: '{candidate}'")
    return None, None

def process_isotope_input(user_input):
    try:
        index = int(user_input) - 1
        search_result = full_element_data[list(full_element_data.keys())[index]]
        return search_result, None
    except (ValueError, IndexError):
        symbol_or_name, mass_number = extract_isotope_factors(user_input)
        if symbol_or_name and mass_number:
            result = recognize_isotope(symbol_or_name, mass_number, user_input)
            if isinstance(result, dict):
                return result, None
            return None, None
        return find_element(user_input)

def safe_format(value, measurement = "", *, placeholder = "None"):
    if value is not None:
        return bold(str(value)) + measurement

    return fore(placeholder, NULL)

# Information
periodica_logo = bold(gradient("Periodica", (156, 140, 255), (140, 255, 245)) if VERBOSE else fore("periodica", BLUE))

program_information = f"""
Welcome to {periodica_logo}!
This CLI provides useful information about the periodic elements, and pretty much everything here was made by the Discord user {bold(fore("Lanzoor", INDIGO))}.
This project started as a fun hobby at around {bold("March 2025")}, but ended up getting taken seriously.
This CLI was built with {fore("Python", CYAN)}, and uses {fore("JSON", YELLOW)} for configuration files / element database.
The vibrant colors and visuals were done with the help of {italic(bold("ANSI escape codes"))}, although you should note that {bold("some terminals may lack support.")}
{dim("(You can disable all styles by using the --raw or -r flag.)")}
There are also other flags you can provide to this CLI. (The ones marked after the slash are shortcut flags. {italic("They behave the same as the original flags.")}) {italic("All flags are case-sensitive.")}

- {bold("--debug")} / -d
- Enable debug mode for testing
- Is a modifier flag
{bold("NOTE: The debug messages intentionally use colors to catch to the eye, even when raw mode is enabled.")}

- {bold("--raw")} / -r
- Disable almost all terminal effects, including truecolor, terminal colors, styles and unicode characters
- Useful for scripting but may need maintenance (output style may and will vary)
- Is a modifier flag

- {bold("--info")} / -i
- Give this information message
- Is a main flag that requires no positional arguments

- {bold("--version")} / -v
- Check the version
- Is a main flag that requires no positional arguments

- {bold("--update")} / -u
- Check for updates
- Is a main flag that requires no positional arguments

- {bold("--export")} [{fore("element", BLUE)}],
  {bold("--export")} [{fore("isotope", GREEN)}] / -x
- Export {fore("element", BLUE)} or {fore("isotope", GREEN)} to a .json file
- Is a main flag with optional positional arguments

- {bold("--compare")} [{fore("factor", RED)}] / -C
- Compare all elements with a factor of {fore("factor", RED)}
- Is a main flag with optional positional arguments

- {bold("--bond-type")} / -B
- Compare two elements and get their bond type
- Is a main flag with optional positional arguments

- {bold("--random")} / -R
- Pick a random element

Also, for flags that import other scripts, debug mode does not apply. Sorry!

Anyways, I hope you enjoy this small CLI. {bold("Please read the README.md file for more information!")}
"""

# Reading json file, and trying to get from GitHub if fails
logger.info("Program initialized.")

try:
    with open(ELEMENT_DATA_FILE, 'r', encoding="utf-8") as file:
        full_element_data = json.load(file)
        logger.info("elements.json file was successfully found.")

    with open(ISOTOPE_DATA_FILE, 'r', encoding="utf-8") as file:
        full_isotope_data = json.load(file)
        logger.info("isotopes.json file was successfully found.")
except json.JSONDecodeError:
    logger.warn("The data JSON files were modified, please do not do so no matter what.")
    print("The data JSON files were modified and malformed. Please do not do so, no matter what.\nThis means you need fresh data JSON files, is it okay for me to get the file for you on GitHub? (y/N)")
    data_malformed = True
except FileNotFoundError:
    logger.warn("The data JSON files were not found.")
    print("The data JSON files were not found. Is it okay for me to get the file for you on GitHub? (y/N)")
    data_malformed = True

if data_malformed:
    confirmation = input("> ").strip().lower()
    if confirmation not in ["y", "yes"]:
        print("Okay, exiting...")
        logger.abort(f"User denied confirmation for fetching the correct data JSON files.")

    element_url = "https://raw.githubusercontent.com/Lanzoor/periodica/main/src/elements.json"
    isotope_url = "https://raw.githubusercontent.com/Lanzoor/periodica/main/src/isotopes.json"

    print(f"(1/2) Getting content from {element_url}.")
    response = get_response(element_url)
    print("(1/2) Successfully got the elements.json file. Replacing it...")
    full_element_data = json.loads(response.text)
    with open(ELEMENT_DATA_FILE, "w", encoding="utf-8") as file:
        file.write(response.text)
    logger.info(f"(1/2) Successfully got the elements.json file from {isotope_url}.")

    print(f"(2/2) Getting content from {isotope_url}.")
    response = get_response(isotope_url)
    print("(2/2) Successfully got the isotopes.json file. Replacing it...")
    full_isotope_data = json.loads(response.text)
    with open(ISOTOPE_DATA_FILE, "w", encoding="utf-8") as file:
        file.write(response.text)
    logger.info(f"(2/2) Successfully got the isotopes.json file from {isotope_url}.")

# Getting element / isotope
try:
    TERMINAL_WIDTH = os.get_terminal_size().columns
    TERMINAL_HEIGHT = os.get_terminal_size().lines
    logger.info(f"Terminal size: {TERMINAL_WIDTH}x{TERMINAL_HEIGHT} (width x height)")
except OSError:
    print(bold("You aren't running this on a terminal, which is very weird. We will try to ignore this issue, and will determine your terminal width as 80. Please move on like nothing ever happened."))
    logger.warn("The script ran without a terminal, so failback to reasonable terminal width variable.")
    TERMINAL_WIDTH = 80
    TERMINAL_HEIGHT = 40

if TERMINAL_WIDTH < 80:
    print(fore(f"You are running this program in a terminal that has a width of {bold(TERMINAL_WIDTH)},\nwhich may be too compact to display and provide the information.\nPlease try resizing your terminal.\nThis will still display content, but it may look broken or unintended.", RED))
    logger.warn("Not enough width for terminal.")

if len(sys.argv) > 1:
    unrecognized_flags = [f for f in separated_flags if f not in valid_flags]
    if unrecognized_flags:
        print("Unrecognizable flags detected. Run the script with the --info flag for more information.")
        logger.abort(f"Unrecognizable flags detected: {unrecognized_flags}")

    modifier_used = [f for f in separated_flags if f in modifier_flags]
    primary_flags = [f for f in separated_flags if f not in modifier_flags]

    logger.info(f"Modifiers: {modifier_used}")
    logger.info(f"Primary flags: {primary_flags}")
    logger.info(f"Positional args: {positional_arguments}")

    create_flag_event("--debug", "-d", callable=enable_debugging)
    create_flag_event("--raw", "-r", callable=enable_raw_output)

    primary_flag = None
    user_input = None

    if len(primary_flags) > 1:
        print("Multiple main flags detected. Run the script with the --info flag for more information.")
        logger.abort(f"Multiple main flags detected: {primary_flags}")
    elif len(primary_flags) == 1:
        primary_flag = primary_flags[0]

        # Case 1: primary flag requires a positional argument
        if primary_flag in positionarg_req_flags:
            if len(positional_arguments) > 1 and primary_flag not in ['-C', '-B', '--compare', '--bond-type']:
                print(fore("Too many positional arguments. Refer to --info.", RED))
                logger.abort("Too many positional arguments.")

            user_input = positional_arguments[0] if positional_arguments else None

        # Case 2: primary flag must not have positional arguments
        elif primary_flag in positionarg_nreq_flags:
            if len(positional_arguments) > 0:
                print(fore("Unexpected positional argument. Refer to --info.", RED))
                logger.abort("Unexpected additional arguments.")

        recognized_flag = (
            create_flag_event("--info", "-i", callable=get_information) or
            create_flag_event("--update", "-u", callable=check_for_updates) or
            create_flag_event("--export", "-x", callable=export_element) or
            create_flag_event("--compare", "-C", callable=compare_by_factor) or
            create_flag_event("--bond-type", "-B", callable=compare_bond_type) or
            create_flag_event("--random", "-R", callable=select_random_element) or
            create_flag_event("--version", "-v", callable=fetch_version)
        )

        if recognized_flag and primary_flag in positionarg_nreq_flags:
            sys.exit(0)

    else:
        if len(positional_arguments) > 1:
            print(fore("Too many positional arguments. Refer to --info.", RED))
            logger.abort("Too many positional arguments.")
        user_input = positional_arguments[0] if positional_arguments else None

    if user_input:
        logger.info(f"Element positional argument entry given: \"{user_input}\"")
        current_element_data, current_element_suggestion = process_isotope_input(user_input)
        if ISOTOPE_LOGIC:
            sys.exit(0)
        if current_element_data is None:
            message = (
                f"Invalid element or isotope."
                f"{' Did you mean \"' + bold(current_element_suggestion) + '\"?' if current_element_suggestion else ' Falling back to interactive input.'}"
            )
            print(fore(message, YELLOW if current_element_suggestion else RED))
            logger.warn("No valid element or isotope provided from argv, fallback to interactive.")
    else:
        logger.warn("Element argument entry not given, falling back to interactive input.")
else:
    logger.warn("No arguments provided, falling back to interactive input.")

if current_element_data is None:
    print(f"Search for an element by name, symbol, or atomic number. {dim(tip)}")
    while True:
        user_input = input("> ").strip().lower()
        logger.info(f"User gave input: \"{user_input}\"")

        check_for_termination(user_input)

        current_element_data, current_element_suggestion = process_isotope_input(user_input)

        if ISOTOPE_LOGIC:
            sys.exit(0)

        if current_element_data is not None:
            break

        message = "Not a valid element or isotope."
        if current_element_suggestion:
            message += f" Did you mean \"{bold(current_element_suggestion)}\"?"
        print(fore(message, YELLOW if current_element_suggestion else RED))

if DEBUG_MODE:
    print("Printing data...")
    pprint(current_element_data, indent = 2, width=TERMINAL_WIDTH, sort_dicts=False, underscore_numbers=True)

# Dividing categories
general = current_element_data["general"]
historical = current_element_data["historical"]
nuclear = current_element_data["nuclear"]
electronic = current_element_data["electronic"]
physical = current_element_data["physical"]
measurements = current_element_data["measurements"]

# General properties
fullname: str = general["fullname"]
symbol: str = general["symbol"]
atomic_number: int = general["atomic_number"]
description: str = general["description"]

description = "\n\n" + "\n\n".join(
    textwrap.fill(paragraph.strip(), width=TERMINAL_WIDTH, initial_indent="    ", subsequent_indent="")
    for paragraph in description.strip().split("\n\n")
)

color: list[int] = general["appearance"]["color"]

phase: str = general["appearance"]["phase"].capitalize()
formatted_phase: str = phase[:]

try:
    formatted_phase = fore(phase, PHASE_TYPE_COLORS[phase])
except KeyError:
    logger.warn(f"Invalid STP phase for {fullname.capitalize()}; Please pay attention.")
    phase = "solid"

try:
    formatted_phase += f" {PHASE_TYPE_SYMBOLS[phase]}" # type: ignore
except (KeyError, TypeError):
    pass

discoverers = historical["discoverers"]
discovery_date = historical["date"]
period: int = general["period"]
group: int = general["group"]
element_type = general["type"]
block = general["block"]
cas_number = general["cas_number"]

periodic_table = [
    ["▪", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", "▪"],
    ["▪", "▪", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", "▪", "▪", "▪", "▪", "▪", "▪"],
    ["▪", "▪", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", "▪", "▪", "▪", "▪", "▪", "▪"],
    ["▪", "▪", "▪", "▪", "▪", "▪", "▪", "▪", "▪", "▪", "▪", "▪", "▪", "▪", "▪", "▪", "▪", "▪"],
    ["▪", "▪", "▪", "▪", "▪", "▪", "▪", "▪", "▪", "▪", "▪", "▪", "▪", "▪", "▪", "▪", "▪", "▪"],
    ["▪", "▪", " ", "▪", "▪", "▪", "▪", "▪", "▪", "▪", "▪", "▪", "▪", "▪", "▪", "▪", "▪", "▪"],
    ["▪", "▪", " ", "▪", "▪", "▪", "▪", "▪", "▪", "▪", "▪", "▪", "▪", "▪", "▪", "▪", "▪", "▪"],
]

lanthanides = [" "] * 4 + ["▪"] * 15
actinides = [" "] * 4 + ["▪"] * 15

if (period != 6 and group != 3) and (period != 7 and group != 3):
    periodic_table = [list(map(dim, symbol)) for symbol in periodic_table]

lanthanides = [dim(symbol) for symbol in lanthanides]
actinides = [dim(symbol) for symbol in actinides]

LANTHANUM = 57
LUTHENIUM = 72
ACTINIUM = 89
LAWRENCIUM = 103

lanthanides_range = range(LANTHANUM, LUTHENIUM + 1)
actinides_range = range(ACTINIUM, LAWRENCIUM + 1)

if atomic_number in lanthanides_range:
    lanthanides[atomic_number - LANTHANUM + 3] = bold(fore("▪", ELEMENT_TYPE_COLORS[element_type]))
elif atomic_number in actinides_range:
    actinides[atomic_number - ACTINIUM + 3] = bold(fore("▪", ELEMENT_TYPE_COLORS[element_type]))
else:
    periodic_table[period - 1][group - 1] = bold(fore("▪", ELEMENT_TYPE_COLORS[element_type]))

entries = [
    fore(name, TURQUOISE if gender == "TURQUOISE" else PINK)
    for name, gender in discoverers.items()
]

discoverers = conjunction_join(entries)

# Nuclear properties
protons = nuclear["protons"]
neutrons = nuclear["neutrons"]
electrons = nuclear["electrons"]
valence_electrons = nuclear["valence_electrons"]
up_quarks = (protons * 2) + neutrons
down_quarks = protons + (neutrons * 2)
mass_number = protons + neutrons
shells = electronic["shells"]
subshells = electronic["subshells"]
isotopes = full_isotope_data[fullname.capitalize()]

possible_shells = "klmnopqrstuvwxyz"
shell_result = ""
for index, electron in enumerate(shells):
    max_capacity = ((index + 1) ** 2) * 2
    if index != len(shells) - 1:
        shell_result += f"{bold(str(electron) + str(possible_shells[index]))} ({electron}/{max_capacity}), "
    else:
        shell_result += f"{bold(fore(str(electron) + str(possible_shells[index]), VALENCE_ELECTRONS_COL))} ({electron}/{max_capacity})"

unpaired_electrons = 0
subshell_capacities = {"s": 2, "p": 6, "d": 10, "f": 14}
orbital_capacity_map = {"s": 1, "p": 3, "d": 5, "f": 7}
subshell_result = ""
pattern = re.compile(r"(\d)([spdf])(\d+)")

for index, subshell in enumerate(subshells):
    if len(subshell) < 3 or not subshell[-1].isdigit():
        logger.warn(f"To the developers, a malformed subshell was detected in {fullname.capitalize()}. Issue: {subshell}")
        continue

    formatted_subshell = subshell[:-1] + (convert_superscripts(subshell[-1]) if VERBOSE else subshell[-1])
    match = pattern.match(subshell)
    if match:
        energy_level, subshell_type, electron_count = match.groups()
        electron_count = int(electron_count)
        max_capacity = subshell_capacities[subshell_type]
        colored_subshell = fore(formatted_subshell, SUBSHELL_COLORS.get(subshell_type, DEFAULT_COLOR))
        colored_subshell = inverse_color(colored_subshell) if index + 1 == len(subshells) else colored_subshell
        subshell_result += f"{colored_subshell} ({electron_count}/{max_capacity}), "
    else:
        subshell_type = subshell[1] if len(subshell) > 1 else 's'
        colored_subshell = fore(formatted_subshell, SUBSHELL_COLORS.get(subshell_type, DEFAULT_COLOR))
        colored_subshell = inverse_color(colored_subshell) if index + 1 == len(subshells) else colored_subshell
        subshell_result += f"{colored_subshell}, "

subshell_result = subshell_result.rstrip(", ")

formatted_lines = []
for subshell_string in subshells:
    match = pattern.fullmatch(subshell_string)
    if not match:
        continue
    energy_level, orbital_type, electron_count = match.groups()
    electron_count = int(electron_count)
    number_of_orbitals = orbital_capacity_map[orbital_type]
    orbitals = [""] * number_of_orbitals

    for index in range(min(electron_count, number_of_orbitals)):
        orbitals[index] = up_arrow
    remaining_electrons = electron_count - number_of_orbitals
    for index in range(number_of_orbitals):
        if remaining_electrons <= 0:
            break
        orbitals[index] += down_arrow
        remaining_electrons -= 1

    orbital_boxes = []
    for orbital in orbitals:
        if orbital == "":
            orbital_boxes.append("[  ]")
        else:
            spins_colored = "".join(
                fore("\u2191", GREEN) if spin == up_arrow else fore("\u2193", RED)
                for spin in orbital
            )
            orbital_boxes.append(f"[{spins_colored}]")

    formatted_line = f"  {energy_level + orbital_type:<4} {' '.join(orbital_boxes)}"
    formatted_lines.append(formatted_line)
    current_unpaired_electrons = sum(1 for orbital in orbitals if orbital == up_arrow or orbital == down_arrow)
    unpaired_electrons += current_unpaired_electrons

subshell_visualisation = "\n".join(formatted_lines)
subshell_examples = "".join([fore(orbital, SUBSHELL_COLORS[orbital]) for orbital in list("spdf")])
pair_determiner = fore("Diamagnetic", VALENCE_ELECTRONS_COL) if unpaired_electrons == 0 else fore("Paramagnetic", ELECTRONEG_COL)

if subshells:
    last_subshell = subshells[-1]
    match = pattern.match(last_subshell)
    if match:
        principal_quantum_number, subshell_type, electron_count = match.groups()
        principal_quantum_number = int(principal_quantum_number)
        electron_count = int(electron_count)
        azimuthal_quantum_number = {"s": 0, "p": 1, "d": 2, "f": 3}[subshell_type]
        magnetic_quantum_number = 0
        spin_quantum_number = "+1/2" if unpaired_electrons % 2 == 1 else "-1/2"
        shielding_constant = calculate_shielding_constant(subshells, last_subshell[:-1])

        effective_nuclear_charge = atomic_number - shielding_constant

        last_subshell = last_subshell[:-1] + convert_superscripts(last_subshell[-1]) if VERBOSE else last_subshell
        last_subshell = fore(last_subshell, SUBSHELL_COLORS.get(subshell_type, (255, 255, 255)))

        subshell_visualisation += f"\n\n      {fore("Valence Subshell", VALENCE_ELECTRONS_COL)} ({inverse_color(last_subshell)}):"
        subshell_visualisation += f"\n        n - {fore('Principal', CYAN)}: {bold(principal_quantum_number)}"
        subshell_visualisation += f"\n        l - {fore('Azimuthal', GREEN)}: {bold(azimuthal_quantum_number)} ({subshell_type} subshell)"
        subshell_visualisation += f"\n        m_l - {fore('Magnetic', YELLOW)}: {bold(magnetic_quantum_number)} (approximated)"
        subshell_visualisation += f"\n        m_s - {fore('Spin', MAGENTA)}: {bold(spin_quantum_number)} ({unpaired_electrons} unpaired electron{'s' if unpaired_electrons != 1 else ''}, {pair_determiner})"
        subshell_visualisation += f"\n        {sigma} - {fore('Shielding Constant', PERIWINKLE)}: {bold(f'{shielding_constant:.2f}')}"
        subshell_visualisation += f"\n        Z_eff - {fore('Effective Nuclear Charge', GOLD)}: {bold(f'{effective_nuclear_charge:.2f}')}"

# Physical properties
melting_point = physical["melt"]
boiling_point = physical["boil"]
atomic_mass = physical["atomic_mass"]
radioactive = general["radioactive"]
half_life = general["half_life"]

# Electronic properties
electronegativity = electronic["electronegativity"]
electron_affinity = electronic["electron_affinity"]
ionization_energy = electronic["ionization_energy"]
oxidation_states = electronic["oxidation_states"]

conductivity_type = electronic["conductivity_type"]

try:
    formatted_conductivity = fore(conductivity_type, CONDUCTIVITY_TYPE_COLORS[conductivity_type])
except KeyError:
    logger.warn(f"Invalid conductivity type found; {conductivity_type}. Please pay attention.")
    formatted_conductivity = bold(conductivity_type)

try:
    formatted_conductivity += f" {CONDUCTIVITY_TYPE_SYMBOLS[conductivity_type]}" # type: ignore
except (KeyError, TypeError):
    pass

# Measurements
radius = measurements["radius"]
hardness = measurements["hardness"]
moduli = measurements["moduli"]
density = measurements["density"]
sound_transmission_speed = measurements["sound_transmission_speed"]

logger.info("Starting output.")

print()
print_header("General")
print()

print(f" 🔡 - Element Name: {bold(fullname)} ({bold(symbol)})")
print(f" Z - Atomic Number: {bold(atomic_number)}")
print(f" 📃 - Description: {description}\n")
print(f" 🔡 - STP Phase: {formatted_phase}")

if color is not None:
    try:
        color_description = general["appearance"]["color_description"]
    except (KeyError, ValueError):
        logger.warn(f"No color description for {fullname.capitalize()} given when the color was present. Please pay attention.")
        color_description = "not given"
    if VERBOSE:
        r, g, b = color
        colored_block = fore(full_block * 2, (r, g, b))
        print(f" 🎨 - Standard Color: {colored_block} ({bold(color_description)})")
    else:
        print(f" 🎨 - Standard Color: {color_description}")
else:
    print(f" 🎨 - Standard Color: {fore("Colorless", NULL)}")

print(f" 🔍 - Discoverer(s): {discoverers}")
print(f" 🔍 - Discovery Date: {bold(discovery_date)}")
print(f" ↔️ - Period (Row): {bold(period)}")
print(f" ↕️ - Group (Column): {bold(group)}")

try:
    print(f" 🎨 - Type: {bold(fore(element_type, ELEMENT_TYPE_COLORS[element_type]))}")
except KeyError:
    logger.warn(f"Invalid element type for {fullname.capitalize()}. Please pay attention.")

print(f" 🧱 - Block: {bold(block)}")
print(f" 📇 - CAS Number: {bold(cas_number)}")

if VERBOSE:
    print()

    print("  ", end="")
    for y in periodic_table:
        for x in y:
            print(x, end=" ")
        print("\n  ", end="")

    print()

    for lanthanide in lanthanides:
        print(lanthanide, end=" ")

    print()

    for actinide in actinides:
        print(actinide, end=" ")

    print()

print()
print_header("Nuclear Properties")
print()

print(f" p{superscript_pos} - {fore('Protons', RED)}: {bold(protons)}")
print(f" n{superscript_zero} - {fore('Neutrons', BLUE)}: {bold(neutrons)}")
print(f" e{superscript_neg} - {fore('Electrons', YELLOW)}: {bold(electrons)}")
print(f" nv - {fore('Valence Electrons', VALENCE_ELECTRONS_COL)}: {bold(valence_electrons)}")

up_quarks_calculation = f"({fore(protons, RED)} * 2) + {fore(neutrons, BLUE)} = {bold(up_quarks)}"
print(f" u - {fore('Up Quarks', GREEN)}: {up_quarks_calculation}")

down_quarks_calculation = f"{fore(protons, RED)} + ({fore(neutrons, BLUE)} * 2) = {bold(down_quarks)}"
print(f" d - {fore('Down Quarks', CYAN)}: {down_quarks_calculation}")

shell_tip = dim(f'(Valence electrons in {fore('yellow', VALENCE_ELECTRONS_COL)})')
print(f" ⚛️ - {fore('Shells', EXCITED)} {shell_tip}:\n    {shell_result}")

subshell_tip = dim(f'(Colored by type: {subshell_examples}, the valence subshell has its color inversed)')
print(f" 🌀 - {fore('Subshells', PERIWINKLE)} {subshell_tip}:\n    {subshell_result}")
print(f"      {bold('Breakdown')}:\n\n{subshell_visualisation}\n")

isotope_tip = dim(f"(Decay processes in {fore("red", RED)} need verification. Do not trust them!)")
print(f" 🪞 - Isotopes ({len(isotopes.keys())}): {isotope_tip}:")

for isotope, information in isotopes.items():
    print()
    print_isotope(isotope, information, fullname)

print()
print_header("Physical Properties")
print()

print(f" 💧 - {fore("Melting Point", MELT_COL)}: {format_temperature(melting_point)}")
print(f" 💨 - {fore("Boiling Point", BOIL_COL)}: {format_temperature(boiling_point)}")
print(f" A - {fore("Mass Number", GOLD)}: {fore(protons, RED)} + {fore(neutrons, BLUE)} = {bold(protons + neutrons)}")
print(f" u - {fore("Atomic Mass", BRIGHT_RED)}: {bold(atomic_mass)}g/mol")
print(f" {emoji_radioactive} - {fore("Radioactive", ORANGE)}: {fore("Yes", GREEN) if radioactive else fore("No", RED)}")
print(f" t1/2 - {fore("Half Life", PERIWINKLE)}: {safe_format(half_life, placeholder="Stable")}")

print()
print_header("Electronic Properties")
print()

print(f" {chi} - {fore("Electronegativity", ELECTRONEG_COL)}: {bold(electronegativity)}")
print(f" EA - {fore("Electron Affinity", EXCITED)}: {format_energy(electron_affinity)}")
print(f" IE - {fore("Ionization Energy", PINK)}: {format_energy(ionization_energy)}")

ionization_energy_series_tip = bold("(THIS IS A VERY HUGE SIMPLIFICATION. Do not rely on them.)")
print(f"      {bold("ESTIMATED")} Ionization Energy Series {ionization_energy_series_tip}:")
print(f"\n{calculate_ionization_series(subshells, atomic_number, ionization_energy)}\n")

if VERBOSE:
    negatives_template = [0, -1, -2, -3, -4, -5]
    positives_template = [1, 2, 3, 4, 5, 6, 7, 8, 9]

    negatives = []
    positives = []

    for state in negatives_template:
        if state in oxidation_states:
            if state == 0:
                negatives.append(bold(fore(state, GREEN)))
            else:
                negatives.append(bold(fore(state, BLUE)))
        else:
            negatives.append(dim(str(state)))

    for state in positives_template:
        if state in oxidation_states:
            positives.append(bold(fore(state, RED)))
        else:
            positives.append(dim(str(state)))

    negatives_result = ", ".join(negatives)
    positives_result = ", ".join(positives)
    oxidation_states_result = f"\n{"   " + negatives_result}\n{"   " + positives_result}\n"
    oxidation_states_tip = dim(f"(Only the ones that have {fore("color", BLUE)} are activated)")
else:
    raw_oxidation_states = map(str, oxidation_states[:])
    raw_oxidation_states = ", ".join(raw_oxidation_states)
    oxidation_states_result = f"\n{raw_oxidation_states}\n"
    oxidation_states_tip = ""

print(f" {emoji_energy} - {fore("Oxidation States", YELLOW)} {oxidation_states_tip}:{oxidation_states_result}")
print(f" c - {fore("Conductivity Type", BRIGHT_BLACK)}: {bold(formatted_conductivity)}")

print()
print_header("Measurements")
print()

print(f" r - {fore("Radius", PINK)}: ")
print(f"   r_calc - Calculated: {safe_format(radius['calculated'], 'pm', placeholder='N/A')}")
print(f"   r_emp - Empirical: {safe_format(radius['empirical'], 'pm', placeholder='N/A')}")
print(f"   r_cov - Covalent: {safe_format(radius['covalent'], 'pm', placeholder='N/A')}")
print(f"   rvdW - Van der Waals: {safe_format(radius['van_der_waals'], 'pm', placeholder='N/A')}\n")
print(f" H - {fore("Hardness", PERIWINKLE)}: ")
print(f"   HB - Brinell: {safe_format(hardness['brinell'], f'kgf/{mm2}')}")
print(f"   H - Mohs: {safe_format(hardness['mohs'], '')}")
print(f"   HV - Vickers: {safe_format(hardness['vickers'], f'kgf/{mm2}')}\n")
print(f" {emoji_exchange} - {fore("Moduli", EXCITED)}: ")
print(f"   K - Bulk Modulus: {safe_format(moduli['bulk'], 'GPa')}")
print(f"   E - Young's Modulus: {safe_format(moduli['young'], 'GPa')}")
print(f"   G - Shear Modulus: {safe_format(moduli['shear'], 'GPa')}")
print(f"   ν - Poisson's Ratio: {safe_format(moduli['poissons_ratio'], '')}\n")
print(f" {rho} - {fore("Density", CYAN)}: ")
print(f"   STP Density: {safe_format(density['STP'], f'kg/{m3}')}")
print(f"   Liquid Density: {safe_format(density['liquid'], f'kg/{m3}')}\n")

print(f" {emoji_speaker} - Speed of Sound Transmission: {bold(sound_transmission_speed)}m/s = {bold(sound_transmission_speed / 1000)}km/s")

print_separator()

logger.info("End of program reached. Aborting...")
sys.exit(0)
