#!/usr/bin/env python3

import platform, pathlib, subprocess, sys, json, os, re, difflib, random, typing, textwrap

try:
    import utils
except ImportError:
    print("The utils helper library was not found. Please ensure all required files are present.")
    sys.exit(1)

from utils.loader import get_config, get_response, Logger
from utils.terminal import RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, BRIGHT_BLACK, BRIGHT_GREEN
from utils.terminal import fore, bold, dim, italic, animate_print, clear_screen, gradient
from pprint import pprint

# Directory paths and variables
VERSION_TUPLE = tuple(map(int, platform.python_version_tuple()))
PERIODICA_DIR = pathlib.Path(__file__).resolve().parent.parent
BUILD_FILE = PERIODICA_DIR / "build.py"
OUTPUT_FILE = PERIODICA_DIR / "src" / "output.json"
CONFIG_FILE = PERIODICA_DIR / "src" / "config.json"
DATA_FILE = PERIODICA_DIR / "src" / "data.json"
PYPROJECT_FILE = PERIODICA_DIR / "pyproject.toml"
VENV_DIR = PERIODICA_DIR / "venv"

EXPORT_ENABLED = False
DEBUG_MODE = False
logger = Logger(debug=DEBUG_MODE)

element_data = None
element_suggestion = ""
recognized_flag = False
elementdata_malformed = False
# greek_symbols = ["α", "β", "γ", "δ", "ε", "ζ", "η", "θ", "ι", "κ", "λ", "μ", "ν", "ξ", "ο", "π", "ρ", "σ", "τ", "υ", "φ", "χ", "ψ", "ω"]

# Get configuration
config = get_config()

superscripts = config["use_superscripts"]
truecolor = config["truecolor"]
isotope_format = config["isotope_format"]
animation_type = config["animation"]
animation_delay = config["animation_delay"]
constant_debugging = config["constant_debugging"]

# Defining custom colors (if truecolor is enabled)
if truecolor:
    VALENCE_ELECTRONS_COL = (248, 255, 166)
    ELECTRONEG_COL = (131, 122, 255)
    MALE = (109, 214, 237)
    FEMALE = (255, 133, 245)
    MELT_COL = (52, 110, 235)
    BOIL_COL = (189, 165, 117)
    ORANGE = (245, 164, 66)
    INDIGO = (94, 52, 235)
    NULL = (115, 255, 225)
    EXCITED = (185, 255, 128)
    PERIWINKLE = (87, 89, 212)
    GOLD = (255, 209, 102)
else:
    VALENCE_ELECTRONS_COL = YELLOW
    ELECTRONEG_COL = BLUE
    MALE = CYAN
    FEMALE = MAGENTA
    MELT_COL = BLUE
    BOIL_COL = YELLOW
    ORANGE = YELLOW
    INDIGO = BLUE
    NULL = CYAN
    EXCITED = GREEN
    PERIWINKLE = CYAN
    GOLD = YELLOW

CUBIC_CENTIMETER = "cm³" if superscripts else "cm3"
CUBIC_METER = "m³" if superscripts else "m3"
SQUARE_MILLIMETER = "mm²" if superscripts else "mm2"

full_data = {}

ELEMENT_TYPE_COLORS = {
	"Reactive nonmetal": (130, 255, 151) if truecolor else BRIGHT_GREEN,
	"Noble gas": YELLOW,
	"Alkali metal": (215, 215, 215) if truecolor else BRIGHT_BLACK,
	"Alkali earth metal": ORANGE,
	"Metalloid": CYAN
}

SUBSHELL_COLORS = {
    's': RED,
    'p': GREEN,
    'd': CYAN,
    'f': MAGENTA
}

SUBSHELL_AZIMUTHALS = {
    "s": 0,
    "p": 1,
    "d": 2,
    "f": 3
}

# Fetch arguments that are not flags (removes --export, --compare, etc.)
def get_positional_args() -> list[str]:
    return [arg for arg in sys.argv[1:] if not arg.startswith("--")]

# The opposite of get_positional_args
def get_flags() -> list[str]:
    return [arg for arg in sys.argv[1:] if arg.startswith("--")]

# Defining flag arguments to use everywhere
flag_arguments = [arg.strip().lower() for arg in get_flags()]
positional_arguments = [arg.strip().lower() for arg in get_positional_args()]

# Unit conversions
def celcius_to_kelvin(celsius):
	return (celsius * 1e16 + 273.15 * 1e16) / 1e16

def celcius_to_fahrenheit(celsius):
	return (celsius * 9 / 5) + 32

def eV_to_kJpermol(eV):
    return eV * 96.485

# Print helpers (they use print instead of animate_print since it takes a long time)
def print_header(title):
    dashes = "-" * (TERMINAL_WIDTH - len(title) - 2)
    print(f"--{bold(title)}{dashes}")

def print_separator():
    print()
    print("-" * TERMINAL_WIDTH)
    print()

def ordinal(number):
    if 10 <= number % 100 <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(number % 10, "th")
    return f"{number}{suffix}"

def parse_electron_configuration(subshells):
    config = []
    pattern = re.compile(r"(\d+)([spdf])(\d+)")
    for subshell in subshells:
        match = pattern.fullmatch(subshell)
        if match:
            quantum_no, azimuthal_no, count = match.groups()
            config.append((int(quantum_no), azimuthal_no, int(count)))
    return config

def calculate_shielding_constant(subshell_list: list[str], target_subshell: str) -> float:
    shielding_constant = 0.0
    target_principal_quantum_number, target_subshell_type = int(target_subshell[0]), target_subshell[1]
    target_azimuthal_quantum_number = SUBSHELL_AZIMUTHALS[target_subshell_type]
    configuration = parse_electron_configuration(subshell_list)

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

def calculate_ionization_series(subshells: list[str], atomic_number: int, ionization_energy: float) -> str:
    lines = []
    config = parse_electron_configuration(subshells)
    RYDBERG_CONSTANT = 13.6

    for index in range(atomic_number):
        last_filled = None
        for idx in range(len(config) - 1, -1, -1):
            quantum_no, azimuthal_no, count = config[idx]
            if count > 0:
                last_filled = (quantum_no, azimuthal_no)
                break

        if last_filled is None:
            break

        subshell_str = f"{last_filled[0]}{last_filled[1]}"
        quantum_target = last_filled[0]
        sigma = calculate_shielding_constant(config, subshell_str)
        Z_eff = atomic_number - sigma

        if index == 0:
            current_IE = ionization_energy
        else:
            current_IE = RYDBERG_CONSTANT * (Z_eff ** 2) / (quantum_target ** 2)

        lines.append(
            f"  - {bold(ordinal(index + 1))} Ionization:\n"
            f"    {fore('Removed', RED)} = {subshell_str}\n"
            f"    σ       = {sigma:.2f}\n"
            f"    Z_eff   = {Z_eff:.2f}\n"
            f"    {fore('IE', FEMALE)}      = {bold(f'{current_IE:.3f}')}{"±30 eV" if index != 0 else "eV"}\n"
        )

        for idx in range(len(config) - 1, -1, -1):
            quantum_no, azimuthal_no, count = config[idx]
            if (quantum_no, azimuthal_no) == last_filled and count > 0:
                config[idx] = (quantum_no, azimuthal_no, count - 1)
                break

    return "\n".join(lines)

def convert_superscripts(text: str) -> str:
    superscript_map = {
        "0": "⁰", "1": "¹", "2": "²", "3": "³", "4": "⁴",
        "5": "⁵", "6": "⁶", "7": "⁷", "8": "⁸", "9": "⁹",
        "+": "⁺", "-": "⁻"
    }
    return "".join(superscript_map.get(char, char) for char in text)

def remove_superscripts(text: str) -> str:
    normal_map = {
        "⁰": "0", "¹": "1", "²": "2", "³": "3", "⁴": "4",
        "⁵": "5", "⁶": "6", "⁷": "7", "⁸": "8", "⁹": "9",
        "⁺": "+", "⁻": "-"
    }
    return "".join(normal_map.get(char, char) for char in text)

def join_with_conjunctions(entries: list) -> str:
    if not entries:
        return ""
    if len(entries) == 1:
        return entries[0]
    if len(entries) == 2:
        return f"{entries[0]} and {entries[1]}"
    return f"{', '.join(entries[:-1])}, and {entries[-1]}"

def create_flag_event(*flags: str, callable):
    for arg in sys.argv[1:]:
        if arg in flags:
            callable()
            return True
    return False

def get_information():
    logger.info("User gave --info flag; redirecting to information logic.")
    animate_print(program_information)
    sys.exit(0)

def configurate():
    logger.info("User gave --init flag; redirecting to another script.")
    import configuration
    sys.exit(0)

def check_for_updates():
    logger.info("User gave --update flag; redirecting to update logic.")
    from update import update_main
    update_main()
    sys.exit(0)

def view_table():
    logger.info("User gave --table flag; redirecting to another logic.")

    COLUMNS = 18 * 4
    ROWS = 7 * 3
    if TERMINAL_WIDTH < COLUMNS:
        animate_print(f"Well, the terminal is way too small to display the table. Please run this on a larger window.\n{bold(f"At least a terminal size of {COLUMNS} x {ROWS} is required to display the content.")}")
        logger.abort("Terminal too small to display the table.")
        sys.exit(0)

    if TERMINAL_HEIGHT < ROWS:
        animate_print(f"Well, the terminal is way too small to display the table. Please run this on a larger window.\n{bold(f"At least a terminal size of {COLUMNS} x {ROWS} is required to display the content.")}")
        logger.abort("Terminal too small to display the table.")
        sys.exit(0)

    clear_screen()

    # TODO: Continue the logic. Way too busy to refactor stuff for now.

    sys.exit(0)

def export_element():
    global EXPORT_ENABLED, positional_arguments

    logger.info("User gave --export flag; redirecting to export logic.")
    EXPORT_ENABLED = True
    sys.argv.remove("--export")

    user_input = positional_arguments[0] if positional_arguments else None

    element = None
    if user_input:
        element, suggestion = process_isotope_input(user_input)
        if element is None and not suggestion:
            animate_print(fore("Could not find that element or isotope. Please enter one manually.", RED))
        else:
            animate_print(fore(f"Could not find that element or isotope. Did you mean {suggestion}?", YELLOW))

    if element is None:
        animate_print(f"Search for an element {italic('to export')} by name, symbol, or atomic number.")
        while element is None:
            user_input = input("> ").strip()
            element, suggestion = process_isotope_input(user_input)
            if element is None and not suggestion:
                animate_print(fore("Could not find that element or isotope. Please enter one manually.", RED))
            else:
                animate_print(fore(f"Could not find that element or isotope. Did you mean {suggestion}?", YELLOW))


    is_isotope = "info" in element and "symbol" in element

    if is_isotope:
        name = element["isotope"]
    else:
        name = element["general"]["fullname"].capitalize()

    animate_print(f"Saving data of {bold(name)} to {OUTPUT_FILE}...")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(
            {
                "symbol": element["symbol"].capitalize(),
                "fullname": element.get("fullname").capitalize(),
                "isotope": element.get("isotope"),
                "data": element.get("info"),
            } if is_isotope else element,
            file,
            indent=4,
            ensure_ascii=False
        )

    animate_print(fore(f"Successfully saved to {OUTPUT_FILE}.", GREEN))
    sys.exit(0)

def compare_by_factor():
    global full_data, positional_arguments
    logger.info("User gave --compare flag; redirecting to another logic.")

    factors = [
        "protons",
        "electrons",
        "neutrons",
        "mass_number",
        "up_quarks",
        "down_quarks"
    ]

    factor_candidate = positional_arguments[0] if positional_arguments else None

    def match_input(data: dict[str, dict], factor):
        try:
            match factor:
                case "protons":
                    return data["nuclear"]["protons"]
                case "electrons":
                    return data["nuclear"]["electrons"]
                case "neutrons":
                    return data["nuclear"]["neutrons"]
                case "mass_number":
                    return data["nuclear"]["protons"] + data["nuclear"]["neutrons"]
                case "up_quarks":
                    return (data["nuclear"]["protons"] * 2) + data["nuclear"]["neutrons"]
                case "down_quarks":
                    return data["nuclear"]["protons"] + (data["nuclear"]["neutrons"] * 2)
        except (KeyError, ValueError):
            return None

    animate_print()
    animate_print(f"Please enter a factor to compare all the elements with. The valid factors are:\n  {', '.join(factors)}")

    while True:
        if factor_candidate and factor_candidate in factors:
            user_factor = factor_candidate
            break

        if factor_candidate:
            suggestion = difflib.get_close_matches(factor_candidate, factors, n=1, cutoff=0.6)
            if suggestion:
                animate_print(fore(f"Not a valid factor. Did you mean \"{bold(suggestion[0])}\"?", YELLOW))
            else:
                animate_print(fore("Not a valid factor. Please provide one manually.", RED))

        factor_candidate = "_".join(input("> ").strip().lower().split(" "))

    animate_print(f"\nComparing all elements by factor {bold(user_factor)}... {dim("(Please note that elements may be missing.)")}\n")

    result: dict[str, str] = {}
    for (name, value) in full_data.items():
        result[name] = match_input(value, user_factor)

    result = dict(sorted(result.items(), key=lambda item: (item[1] is None, item[1])))
    max_value = max(filter(lambda value: isinstance(value, (int, float)), result.values()), default=1)

    for (name, value) in result.items():
        if value is not None:
            padding = 25
            bar_space = max(TERMINAL_WIDTH - padding, 10)
            bar_length = int((value / max_value) * bar_space)
            bar = fore("█" * bar_length, CYAN)
            animate_print(f"{name:<12} {str(value):<4} [{bar}]")

    animate_print()
    sys.exit(0)

def compare_bond_type():
    global full_data, positional_arguments
    logger.info("User gave --bond-type flag; redirecting to bond type logic.")

    primary_element = None
    secondary_element = None

    if len(positional_arguments) >= 2:
        primary_element, _ = find_element(positional_arguments[0])
        secondary_element, _ = find_element(positional_arguments[1])

        if primary_element is None or secondary_element is None:
            animate_print(fore("One or both elements could not be resolved from the arguments. Please provide them manually.", YELLOW))
            primary_element = None
            secondary_element = None
        else:
            logger.info(f"Resolved both elements from CLI args: {positional_arguments[0]}, {positional_arguments[1]}")

    if primary_element is None:
        animate_print()
        animate_print(f"Search for the primary element {italic('to compare the bond type')} with by name, symbol, or atomic number.")
        while True:
            user_input = input("> ").strip().lower()
            logger.info(f"Primary input: \"{user_input}\"")
            primary_element, suggestion = find_element(user_input)
            if primary_element:
                break
            if suggestion:
                animate_print(fore(f"Not a valid element. Did you mean \"{bold(suggestion)}\"?", YELLOW))
            else:
                animate_print(fore(f"Not a valid element.", RED))

    primary_element_name = primary_element["general"]["fullname"]

    if secondary_element is None:
        animate_print()
        animate_print(f"Now, please enter the secondary element {italic('to compare the bond type')} with {bold(primary_element_name)}.")
        while True:
            user_input = input("> ").strip().lower()
            logger.info(f"Secondary input: \"{user_input}\"")
            secondary_element, suggestion = find_element(user_input)
            if secondary_element:
                break
            if suggestion:
                animate_print(fore(f"Not a valid element. Did you mean \"{bold(suggestion)}\"?", YELLOW))
            else:
                animate_print(fore(f"Not a valid element.", RED))

    secondary_element_name = secondary_element["general"]["fullname"]
    primary_en = primary_element["electronic"]["electronegativity"]
    secondary_en = secondary_element["electronic"]["electronegativity"]

    if primary_en is None or secondary_en is None:
        animate_print(fore("Failed to fetch bond type; one or both elements lack electronegativity values (likely inert).", YELLOW))
        sys.exit(0)

    diff = abs(primary_en - secondary_en)
    if diff < 0.4:
        bond_type_str = fore("Nonpolar Covalent", BLUE) + " -"
    elif diff < 1.7:
        bond_type_str = fore("Polar Covalent", YELLOW) + " δ"
    else:
        bond_type_str = fore("Ionic", RED) + " →"

    animate_print()
    animate_print(f"Primary element ({primary_element_name})'s electronegativity: {bold(primary_en)}")
    animate_print(f"Secondary element ({secondary_element_name})'s electronegativity: {bold(secondary_en)}")
    animate_print(f"Difference: {primary_en} - {secondary_en} = ≈{bold(f'{diff:.3f}')}")
    animate_print(f"Bond type: {bond_type_str} (According to Pauling's Electronegativity Method)")
    animate_print()
    sys.exit(0)

def select_random_element():
    global element_data
    animate_print()
    animate_print("Picking a random element...")
    logger.info("Picking a random element...")

    element_data = random.choice(list(full_data.values()))
    animate_print(f"I pick {bold(element_data["general"]["fullname"])} for you!")
    logger.info(f"Picked {element_data["general"]["fullname"]} as a random element.")

def enable_debugging():
    global DEBUG_MODE, logger
    DEBUG_MODE = True
    animate_print(gradient("Debug mode enabled. Have fun...", ELECTRONEG_COL, NULL))

    logger = Logger(debug=DEBUG_MODE)
    logger.info("Enabled debug mode.")

    logger.info(f"Configuration overview: superscripts={superscripts}, truecolor={truecolor}, "
                f"isotope_format={isotope_format}, animation={animation_type}, "
                f"animation_delay={animation_delay}s")

if "--debug" in flag_arguments or constant_debugging:
    enable_debugging()

def fetch_version():
    global PYPROJECT_FILE
    from update import fetch_toml

    logger.info("User gave --version flag; showing version information.")

    local_version = fetch_toml()

    animate_print(f"Version: {local_version}")
    animate_print(f"Python Interpreter: {".".join(platform.python_version_tuple())}")

    sys.exit(0)

# Extract symbol and number from an isotope
def match_isotope_input(user_input: str) -> typing.Tuple[str | None, str | None]:
    match = re.match(r"^(\d+)([A-Za-z]+)$", user_input)
    if match:
        return match.group(2), match.group(1)
    match = re.match(r"^([A-Za-z]+)[\s\-]*(\d+)$", user_input)
    if match:
        return match.group(1), match.group(2)
    return None, None

def print_isotope(norm_iso, info, fullname):
    global animation_delay
    animation_delay /= 4
    animate_print()

    match = re.match(r"^(\d+)\s*([A-Za-z]+)$", remove_superscripts(norm_iso))
    display_name = format_isotope(norm_iso, fullname) if match else norm_iso

    name_display = f" ({info['name']})" if 'name' in info else ""
    animate_print(f"  - {bold(display_name)}{name_display}:")

    protons = info['protons']
    neutrons = info['neutrons']
    animate_print(f"      p{convert_superscripts('+')}, e{convert_superscripts('-')} - {fore('Protons', RED)} and {fore('Electrons', YELLOW)}: {bold(protons)}")
    animate_print(f"      n{'⁰' if superscripts else ''} - {fore('Neutrons', BLUE)}: {bold(neutrons)}")

    up_quarks = protons * 2 + neutrons
    down_quarks = protons + neutrons * 2
    animate_print(f"      u - {fore('Up Quarks', GREEN)}: ({fore(protons, RED)} * 2) + {fore(neutrons, BLUE)} = {bold(up_quarks)}")
    animate_print(f"      d - {fore('Down Quarks', CYAN)}: {fore(protons, RED)} + ({fore(neutrons, BLUE)} * 2) = {bold(down_quarks)}")

    half_life = info.get('half_life')
    animate_print(f"      t1/2 - Half Life: {bold(half_life) if half_life else fore('Stable', NULL)}")
    animate_print(f"      u - Isotope Weight: {bold(info['isotope_weight'])}g/mol")

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
                chance = fore("(Not proven)", RED)
            products = branch.get("product", [])
            if not isinstance(products, list):
                products = [str(products)]
            out = ", ".join(bold(format_isotope(product, fullname)) for product in products)
            arrow = "->" if products else ""

            animate_print(f"{padding}{bold(display_name)} -> {bold(mode)} {arrow} {out} {chance}")

    if isinstance(info.get("decay"), list):
        animate_print("      ⛓️ - Possible Decays:")
        show_decay(info["decay"])

    if isinstance(info.get("metastable"), dict):
        animate_print(f"      m - {fore("Metastable Isotopes", EXCITED)}:")
        for state, data in info["metastable"].items():
            display_meta = format_isotope(norm_iso, fullname, metastable=state)
            animate_print(f"        {bold(display_meta)}:")
            if "half_life" in data:
                animate_print(f"          t1/2 - Half Life: {bold(data['half_life'])}")
            animate_print(f"          ⚡️ - Excitation Energy: {bold(data['energy'])}keV")
            if "decay" in data:
                animate_print("          ⛓️ - Possible Decays:")
                show_decay(data["decay"], indent=14)

    animation_delay *= 4

# Formats an isotope respecting the isotope format
def format_isotope(norm_iso, fullname, *, metastable = ""):
    global isotope_format

    match = re.match(r"^(\d+)\s*([A-Za-z]+)$", remove_superscripts(norm_iso))
    if not match:
        return norm_iso
    else:
        number, symbol = match.groups()
        symbol = symbol.capitalize()
        if isotope_format == "fullname-number":
            return f"{fullname.capitalize()}-{number}{metastable}"
        elif isotope_format == "symbol-number":
            return f"{symbol}-{number}{metastable}"
        elif isotope_format == "numbersymbol":
            number = convert_superscripts(str(number)) if superscripts else number
            return f"{number}{metastable}{symbol}"
        elif isotope_format == "number-symbol":
            number = convert_superscripts(str(number)) if superscripts else number
            return f"{number}{metastable}-{symbol}"
        else:
            return f"{symbol}-{number}{metastable}"

def find_isotope(element_identifier, mass_number, search_query):
    element_identifier = element_identifier.lower()
    search_query = search_query.lower()
    logger.info(f"Searching for isotope: {element_identifier}, mass number: {mass_number}, query: {search_query}")

    for element_data in full_data.values():
        element_symbol = element_data["general"]["symbol"].lower()
        element_name = element_data["general"]["fullname"].lower()

        if element_identifier not in (element_symbol, element_name):
            continue

        logger.info(f"Element match found for '{element_identifier}': {element_name} ({element_symbol})")
        return search_isotope(
            element_data["nuclear"]["isotopes"],
            element_symbol,
            element_name,
            mass_number,
            search_query
        )

    logger.warn(f"No element found for symbol or name: {element_identifier}")
    return False

def search_isotope(isotopes, element_symbol, element_name, mass_number, search_query):
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
            print_separator()
            print_isotope(isotope, isotope_info, element_name)
            print_separator()
            return True

    logger.warn(f"No isotope match found for mass number {mass_number} in element {element_name}")
    return False

def normalize_isotope(isotope):
    match = re.match(r"^(.*?)(?:\s*-\s*.*)?$", isotope)
    normalized = match.group(1) if match else isotope
    return remove_superscripts(normalized)

def find_element(candidate) -> typing.Tuple[dict | None, str | None]:
    logger.info(f"Searching for element match: {candidate}")
    candidate = candidate.lower()
    possible_names = []

    for _, element_candidate in enumerate(full_data.values()):
        name = element_candidate["general"]["fullname"].lower()
        symbol = element_candidate["general"]["symbol"].lower()
        atomic_number = str(element_candidate["general"]["atomic_number"])

        possible_names.extend([name, symbol])

        if candidate in (name, symbol, atomic_number):
            logger.info(f"Exact match found: {name} ({symbol})")
            return element_candidate, None

    suggestion = difflib.get_close_matches(candidate, possible_names, n=1, cutoff=0.6)
    if suggestion:
        logger.warn(f"No direct match found for '{candidate}'. Found a close match; '{suggestion[0]}'?")
        return None, suggestion[0]

    logger.warn(f"No match or suggestion found for input: '{candidate}'")
    return None, None

def process_isotope_input(user_input):
    try:
        index = int(user_input) - 1
        search_result = full_data[list(full_data.keys())[index]]
        return search_result, None
    except (ValueError, IndexError):
        symbol_or_name, mass_number = match_isotope_input(user_input)
        if symbol_or_name and mass_number:
            result = find_isotope(symbol_or_name, mass_number, user_input)
            if isinstance(result, dict):
                return result, None
            return None, None
        return find_element(user_input)

def safe_format(value, measurement, placeholder = "None"):
    if value is not None:
        return bold(str(value)) + measurement

    return fore(placeholder, NULL)

# Virtual environment validation
if VERSION_TUPLE < (3, 11, 0):
    print("You are running this script with an outdated Python interpreter. Please update your Python interpreter if needed.")
    sys.exit(0)

if not VENV_DIR.is_dir():
    print("The virtual environment was not found. Should I run the build script for you? (Y/n)")

    confirmation = input("> ").strip().lower()
    if confirmation not in ["y", "yes", ""]:
        print("You denied the file execution. Please run the build script yourself.")
        sys.exit(0)
    if BUILD_FILE.is_file():
        subprocess.run([sys.executable, str(BUILD_FILE)], check=True)
        sys.exit(0)
    else:
        print("The build script was not found. Please read the README.md for more information. (If that exists, that is.)")

# Other important variables and functions
match random.randint(0, 3):
    case 0:
        tip = "(Tip: You can give this program argv to directly search an element from there. You can even give argv to the periodica.sh file too!)"
    case 1:
        tip = "(Tip: Run this script with the --info flag to get information about flags.)"
    case 2:
        tip = "(Tip: Run this script with the --init flag to configure options like using superscripts.)"
    case 3:
        tip = ""
    case _:
        tip = ""

periodica_logo = bold(gradient("Periodica", (156, 140, 255), (140, 255, 245)) if config['truecolor'] else fore("periodica", BLUE))

program_information = f"""
Welcome to {periodica_logo}!
This CLI provides useful information about the periodic elements, and pretty much everything here was made by the Discord user {bold(fore("Lanzoor", INDIGO))}!
This project started as a fun hobby at around {bold("March 2025")}, but ended up getting taken seriously.
This CLI was built with {fore("Python", CYAN)}, and uses {fore("JSON", YELLOW)} for configuration files / element database.
The vibrant colors and visuals were done with the help of {italic(bold("ANSI escape codes"))}, although you should note that {bold("some terminals may not have truecolor support.")}
{dim("(You can disable this anytime in the config.json file, or using the --init flag.)")}
There are also other flags you can provide to this CLI.

- {bold("--debug")} - Enable debug mode for testing (always the first priority)
- {bold("--info")} - Give this information message
- {bold("--version")} - Check the version
- {bold("--init")} - Edit the settings
- {bold("--update")} - Check for updates
- {bold("--table")} - View the periodic table
- {bold("--export")} {fore("element", BLUE)},
  {bold("--export")} {fore("isotope", GREEN)} - Export {fore("element", BLUE)} or {fore("isotope", GREEN)} to a .json file
- {bold("--compare")} {fore("factor", RED)} - Compare all elements with a factor of {fore("factor", RED)}
- {bold("--bond-type")} - Compare two elements and get their bond type
- {bold("--random")} - Pick a random element

Also, for flags that import other scripts, debug mode does not apply. Sorry!

Anyways, I hope you enjoy this small CLI. {bold("Please read the README.md file for more information!")}
"""

# Reading json file, and trying to get from GitHub if fails

logger.info("Program initialized.")

try:
    with open(DATA_FILE, 'r', encoding="utf-8") as file:
        full_data = json.load(file)
        logger.info("data.json file was successfully found.")
except json.JSONDecodeError:
    logger.warn("data.json file was modified, please do not do so no matter what.")
    animate_print("The data.json file was modified and malformed. Please do not do so, no matter what.\nThis means you need a fresh new data.json file, is it okay for me to get the file for you on GitHub? (y/N)")
    elementdata_malformed = True
except FileNotFoundError:
    logger.warn("data.json file was not found.")
    animate_print("The data.json file was not found. Is it okay for me to get the file for you on GitHub? (y/N)")
    elementdata_malformed = True

if elementdata_malformed:
    confirmation = input("> ").strip().lower()
    if confirmation not in ["y", "yes"]:
        animate_print("Okay, exiting...")
        logger.abort("User denied confirmation for fetching the data.json file.")

    url = "https://raw.githubusercontent.com/Lanzoor/periodictable/main/src/data.json"
    animate_print(f"Getting content from {url}, this should not take a while...")

    response = get_response(url)

    animate_print("Successfully got the data.json file! Replacing it...")

    full_data = json.loads(response.text)
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        file.write(response.text)

    logger.info(f"Successfully got the data.json file from {url}.")

# Getting element / isotope

try:
    TERMINAL_WIDTH = os.get_terminal_size().columns
    TERMINAL_HEIGHT = os.get_terminal_size().lines
except OSError:
    animate_print(bold("What?? So apparently, you aren't running this on a terminal, which is very weird. We will try to ignore this issue, and will determine your terminal width as 80. Please move on and ignore this message."))
    logger.warn("The script ran without a terminal, so failback to reasonable terminal width variable.")
    TERMINAL_WIDTH = 80
    TERMINAL_HEIGHT = 40

if TERMINAL_WIDTH <= 80:
    animate_print(fore(f"You are running this program in a terminal that has a width of {bold(TERMINAL_WIDTH)},\nwhich may be too compact to display and provide the information.\nPlease try resizing your terminal.", RED))
    logger.warn("Not enough width for terminal.")

if len(sys.argv) > 1:
    valid_flag_names = [
        "debug", "info", "init", "update", "table", "export",
        "compare", "bond-type", "random", "version"
    ]

    flags_that_require_position_argument = [
        "export", "compare", "bond-type"
    ]

    valid_flags = ["--" + flag for flag in valid_flag_names]

    flag_arguments = get_flags()
    positional_arguments = get_positional_args()
    primary_flags = [flag for flag in flag_arguments if flag != "--debug"]

    user_input = None

    if len(primary_flags) == 0:
        # No flags provided — treat as standalone element/isotope lookup
        user_input = positional_arguments[0] if positional_arguments else None
    elif len(primary_flags) != 1 or any(flag not in valid_flags for flag in primary_flags):
        animate_print("Malformed flags structure. Run the script with the --info flag for more information.")
        logger.abort("Unrecognizable or multiple main flags detected.")
    else:
        primary_flag = primary_flags[0]
        if primary_flag.replace("--", "") not in flags_that_require_position_argument and len(positional_arguments) > 0:
            animate_print("Unexpected positional argument. Refer to --info.")
            logger.abort("Unexpected additional arguments.")

    recognized_flag = (
        create_flag_event("--info", callable=get_information) or
        create_flag_event("--init", callable=configurate) or
        create_flag_event("--update", callable=check_for_updates) or
        create_flag_event("--table", callable=view_table) or
        create_flag_event("--export", callable=export_element) or
        create_flag_event("--compare", callable=compare_by_factor) or
        create_flag_event("--bond-type", callable=compare_bond_type) or
        create_flag_event("--random", callable=select_random_element) or
        create_flag_event("--version", callable=fetch_version)
    )

    if not recognized_flag:
        if not user_input:
            animate_print(fore("No valid element or isotope provided. Falling back to interactive input.", RED))
            logger.warn("Argv missing valid content, fallback to interactive.")
        else:
            logger.info(f"User gave argv: \"{user_input}\"")
            element_data, element_suggestion = process_isotope_input(user_input)

            if element_data is None:
                message = f"Invalid argv.{' Did you mean \"' + bold(element_suggestion) + '\"?' if element_suggestion else ' Falling back to interactive input.'}"
                animate_print(fore(message, YELLOW if element_suggestion else RED))
                logger.warn("Argv invalid, fallback to interactive.")
else:
    logger.warn("Argument not given, falling back to interactive input.")

if element_data is None:
    animate_print(f"Search for an element by name, symbol, or atomic number. {dim(tip)}")
    while True:
        user_input = input("> ").strip().lower()
        logger.info(f"User gave input: \"{user_input}\"")

        element_data, element_suggestion = process_isotope_input(user_input)

        if element_data is not None:
            break

        message = "Not a valid element or isotope."
        if element_suggestion:
            message += f" Did you mean \"{bold(element_suggestion)}\"?"
        animate_print(fore(message, YELLOW if element_suggestion else RED))

if DEBUG_MODE:
    animate_print("Printing data...")
    pprint(element_data, indent = 2, width=TERMINAL_WIDTH, sort_dicts=False, underscore_numbers=True, depth=float("inf"))

# Dividing categories

general = element_data["general"]
historical = element_data["historical"]
nuclear = element_data["nuclear"]
electronic = element_data["electronic"]
physical = element_data["physical"]
measurements = element_data["measurements"]

# General properties

fullname = general["fullname"]
symbol = general["symbol"]
atomic_number = general["atomic_number"]
description = general["description"]

description = "\n\n" + "\n\n".join(
    textwrap.fill(paragraph.strip(), width=TERMINAL_WIDTH, initial_indent="    ", subsequent_indent="")
    for paragraph in description.strip().split("\n\n")
)

discoverers = historical["discoverers"]
discovery_date = historical["date"]
period = general["period"]
group = general["group"]
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
    lanthanides[atomic_number - LANTHANUM + 3] = fore("▪", ELEMENT_TYPE_COLORS[element_type])
elif atomic_number in actinides_range:
    actinides[atomic_number - ACTINIUM + 3] = fore("▪", ELEMENT_TYPE_COLORS[element_type])
else:
    periodic_table[period - 1][group - 1] = fore("▪", ELEMENT_TYPE_COLORS[element_type])

entries = [
    bold(fore(name, MALE if gender == "male" else FEMALE))
    for name, gender in discoverers.items()
]

discoverers = join_with_conjunctions(entries)

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
isotopes = nuclear["isotopes"]

possible_shells = "klmnopqrstuvwxyz"
shell_result = ""
for index, electron in enumerate(shells):
    max_capacity = ((index + 1) ** 2) * 2
    if index != len(shells) - 1:
        shell_result += f"{bold(str(electron) + str(possible_shells[index]))} ({electron}/{max_capacity}), "
    else:
        shell_result += f"{bold(fore(electron, VALENCE_ELECTRONS_COL) + fore(possible_shells[index], VALENCE_ELECTRONS_COL))} ({electron}/{max_capacity})"
unpaired_electrons = 0
subshell_capacities = {"s": 2, "p": 6, "d": 10, "f": 14}
orbital_capacity_map = {"s": 1, "p": 3, "d": 5, "f": 7}

subshell_result = ""
pattern = re.compile(r"(\d)([spdf])(\d+)")

for subshell in subshells:
    if len(subshell) < 3 or not subshell[-1].isdigit():
        logger.warn(f"To the developers, a malformed subshell was detected in {fullname.capitalize()}. Issue: {subshell}")
        continue

    formatted_subshell = subshell[:-1] + (convert_superscripts(subshell[-1]) if superscripts else subshell[-1])
    match = pattern.match(subshell)

    if match:
        energy_level, subshell_type, electron_count = match.groups()
        electron_count = int(electron_count)
        max_capacity = subshell_capacities[subshell_type]
        colored_subshell = fore(formatted_subshell, SUBSHELL_COLORS.get(subshell_type, (255, 255, 255)))
        subshell_result += f"{bold(colored_subshell)} ({electron_count}/{max_capacity}), "
    else:
        subshell_type = subshell[1] if len(subshell) > 1 else 's'
        colored_subshell = fore(formatted_subshell, SUBSHELL_COLORS.get(subshell_type, (255, 255, 255)))
        subshell_result += f"{bold(colored_subshell)}, "

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
        orbitals[index] = "↑"
    remaining_electrons = electron_count - number_of_orbitals
    for index in range(number_of_orbitals):
        if remaining_electrons <= 0:
            break
        orbitals[index] += "↓"
        remaining_electrons -= 1

    orbital_boxes = []
    for orbital in orbitals:
        if orbital == "":
            orbital_boxes.append("[  ]")
        else:
            spins_colored = "".join(
                fore("\u2191", GREEN) if spin == "↑" else fore("\u2193", RED)
                for spin in orbital
            )
            orbital_boxes.append(f"[{spins_colored}]")

    formatted_line = f"{energy_level + orbital_type:<4} {' '.join(orbital_boxes)}"
    formatted_lines.append(formatted_line)
    current_unpaired_electrons = sum(1 for orbital in orbitals if orbital == "↑" or orbital == "↓")
    unpaired_electrons += current_unpaired_electrons

subshell_visualisation = "\n".join(formatted_lines)
subshell_examples = "".join([fore(orbital, SUBSHELL_COLORS[orbital]) for orbital in list("spdf")])
pair_determiner = fore("Diamagnetic", VALENCE_ELECTRONS_COL) if unpaired_electrons == 0 else fore("Paramagnetic", ELECTRONEG_COL)

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

conductivity_type = electronic["conductivity_type"]

# Measurements
radius = measurements["radius"]
hardness = measurements["hardness"]
moduli = measurements["moduli"]
density = measurements["density"]
sound_transmission_speed = measurements["sound_transmission_speed"]

logger.info("Starting output.")

animate_print()
print_header("General")
animate_print()

animate_print(f" 🔡 - Element Name: {bold(fullname)} ({bold(symbol)})")
animate_print(f" Z - Atomic Number: {bold(atomic_number)}")
animate_print(f" 📃 - Description: {description}\n")
animate_print(f" 🔍 - Discoverer(s): {discoverers}")
animate_print(f" 🔍 - Discovery Date: {bold(discovery_date)}")
animate_print(f" ↔️ - Period (Row): {bold(period)}")
animate_print(f" ↕️ - Group (Column): {bold(group)}")
animate_print(f" 🎨 - Type: {fore(element_type, ELEMENT_TYPE_COLORS[element_type])}")
animate_print(f" 🧱 - Block: {bold(block)}")
animate_print(f" 📇 - CAS Number: {bold(cas_number)}")

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

animate_print(f" p{convert_superscripts("+")} - {fore("Protons", RED)}: {bold(protons)}")
animate_print(f" n{"⁰" if superscripts else ""} - {fore("Neutrons", BLUE)}: {bold(neutrons)}")
animate_print(f" e{convert_superscripts("-")} - {fore("Electrons", YELLOW)}: {bold(electrons)}")
animate_print(f" nv - {fore("Valence Electrons", VALENCE_ELECTRONS_COL)}: {bold(valence_electrons)}")
animate_print(f" u - {fore("Up Quarks", GREEN)}: ({fore(protons, RED)} * 2) + {fore(neutrons, BLUE)} = {bold(up_quarks)}")
animate_print(f" d - {fore("Down Quarks", CYAN)}: ({fore(protons, RED)} + ({fore(neutrons, BLUE)} * 2) = {bold(down_quarks)}")
animate_print(f" ⚛️ - {fore("Shells", EXCITED)} {dim(f"(The electron in {fore("yellow", VALENCE_ELECTRONS_COL)} is the valence electron)")}:\n    {shell_result}")
animate_print(f" 🌀 - {fore("Subshells", PERIWINKLE)} {dim(f"(Subshells are colored by their type. {subshell_examples})")}:\n    {subshell_result}")
animate_print(f"      Breakdown:\n{subshell_visualisation}")
animate_print(f"      Total unpaired electrons: {bold(unpaired_electrons)}, {pair_determiner}")
animate_print(f"      Spin: {unpaired_electrons} * 0.5 = {bold(unpaired_electrons * 0.5)}")
animate_print(f" 🪞 - Isotopes ({len(isotopes.keys())}): {dim(f"(Decay processes in {fore("red", RED)} need verification. Do not trust them!)")}:")

for isotope, information in isotopes.items():
    print_isotope(isotope, information, fullname)

animate_print()
print_header("Physical Properties")
animate_print()

animate_print(f" 💧 - {fore("Melting Point", MELT_COL)}: {bold(melting_point)}°C = {bold(celcius_to_fahrenheit(melting_point))}°F = {bold(celcius_to_kelvin(melting_point))}K")
animate_print(f" 💨 - {fore("Boiling Point", BOIL_COL)}: {bold(boiling_point)}°C = {bold(celcius_to_fahrenheit(boiling_point))}°F = {bold(celcius_to_kelvin(boiling_point))}K")
animate_print(f" A - {fore("Mass Number", GOLD)}: {fore(protons, RED)} + {fore(neutrons, BLUE)} = {bold(protons + neutrons)}")
animate_print(f" u - Atomic Mass: {bold(atomic_mass)}g/mol")
animate_print(f" ☢️ - {fore("Radioactive", ORANGE)}: {fore("Yes", GREEN) if radioactive else fore("No", RED)}")
animate_print(f" t1/2 - Half Life: {bold(half_life if not (half_life is None) else fore("Stable", CYAN))}")

animate_print()
print_header("Electronic Properties")
animate_print()

animate_print(f" χ - {fore("Electronegativity", ELECTRONEG_COL)}: {bold(electronegativity)}")
animate_print(f" EA - Electron Affinity: {bold(electron_affinity)}eV = {bold(eV_to_kJpermol(electron_affinity))}kJ/mol")
animate_print(f" IE - {fore("Ionization Energy", FEMALE)}: {bold(ionization_energy)}eV = {bold(eV_to_kJpermol(ionization_energy))}kJ/mol")
animate_print(f"      {bold("ESTIMATED")} Ionization Energy Series {bold("(THIS IS A VERY HUGE SIMPLIFICATION. Do not rely on them.)")}: ")
animate_print(f"\n{calculate_ionization_series(subshells, atomic_number, ionization_energy)}\n")

animate_print(f" ⚡️ - {fore("Oxidation States", YELLOW)} {dim(f"(Only the ones that have {fore("color", BLUE)} are activated)")}:\n{"   " + negatives_result}\n{"   " + positives_result}\n")
animate_print(f" ⚡️ - {fore("Conductivity Type", BRIGHT_BLACK)}: {bold(conductivity_type)}")

animate_print()
print_header("Measurements")
animate_print()

animate_print(f" r - {fore("Radius", FEMALE)}: ")
animate_print(f"   r_calc - Calculated: {safe_format(radius['calculated'], 'pm', 'N/A')}")
animate_print(f"   r_emp - Empirical: {safe_format(radius['empirical'], 'pm', 'N/A')}")
animate_print(f"   r_cov - Covalent: {safe_format(radius['covalent'], 'pm', 'N/A')}")
animate_print(f"   rvdW - Van der Waals: {safe_format(radius['van_der_waals'], 'pm', 'N/A')}\n")
animate_print(f" H - {fore("Hardness", PERIWINKLE)}: ")
animate_print(f"   HB - Brinell: {safe_format(hardness['brinell'], f'kgf/{SQUARE_MILLIMETER}')}")
animate_print(f"   H - Mohs: {safe_format(hardness['mohs'], '')}")
animate_print(f"   HV - Vickers: {safe_format(hardness['vickers'], f'kgf/{SQUARE_MILLIMETER}')}\n")
animate_print(f" 🔃 - {fore("Moduli", EXCITED)}: ")
animate_print(f"   K - Bulk Modulus: {safe_format(moduli['bulk'], 'GPa')}")
animate_print(f"   E - Young's Modulus: {safe_format(moduli['young'], 'GPa')}")
animate_print(f"   G - Shear Modulus: {safe_format(moduli['shear'], 'GPa')}")
animate_print(f"   ν - Poisson's Ratio: {safe_format(moduli['poissons_ratio'], '')}\n")
animate_print(" ρ - Density: ")
animate_print(f"   STP Density: {safe_format(density['STP'], f'kg/{CUBIC_METER}')}")
animate_print(f"   Liquid Density: {safe_format(density['liquid'], f'kg/{CUBIC_METER}')}\n")

animate_print(f" 📢 - Speed of Sound Transmission: {bold(sound_transmission_speed)}m/s = {bold(sound_transmission_speed / 1000)}km/s")

print_separator()

logger.info("End of program reached. Aborting...")
sys.exit(0)
