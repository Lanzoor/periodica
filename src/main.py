import logging, json, os, re, sys, logging, difflib, colorsys, random, re, sys, time

with open('./execution.log', 'w', encoding="utf-8"):
    pass

logging.basicConfig(
    filename='./execution.log',
    filemode='w',
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

logging.info("Program initiallized.")

default_options = {
    "use_superscript": True,
    "truecolor": True,
    "isotope_format": "fullname-number",
}

valid_formats = [
    "fullname-number",
    "symbol-number",
    "numbersymbol"
]

try:
    with open('./config.json', 'r', encoding="utf-8") as file:
        config = json.load(file)
        logging.info("The configuration file was found.")
except json.JSONDecodeError:
    with open('./config.json', 'w', encoding="utf-8") as file:
        config = default_options
        file.write(json.dumps(default_options))
        logging.info("Overwrited configuration file since it was malformed.")
except FileNotFoundError:
    with open('./config.json', 'w', encoding="utf-8") as file:
        config = default_options
        file.write(json.dumps(default_options))
        logging.info("Created a new configuration file, since it didn't exist.")

for key, value in default_options.items():
    if key == "isotope_format":
        if config[key] not in valid_formats:
            config[key] = value
    else:
        config.setdefault(key, value)

# Color Configs

BLACK = 0
RED = 1
GREEN = 2
YELLOW = 3
BLUE = 4
MAGENTA = 5
CYAN = 6
WHITE = 7
DEFAULT_COLOR = 9

VALENCE_ELECTRONS_COL = (248, 255, 166) if config["truecolor"] else YELLOW
UP_QUARKS_COL = (122, 255, 129) if config["truecolor"] else GREEN
DOWN_QUARKS_COL = (230, 156, 60) if config["truecolor"] else CYAN
MALE = (109, 214, 237) if config["truecolor"] else CYAN
FEMALE = (255, 133, 245) if config["truecolor"] else MAGENTA
NULL_COL = (90, 232, 227) if config["truecolor"] else CYAN
MELT_COL = (52, 110, 235) if config["truecolor"] else BLUE
BOIL_COL = (189, 165, 117) if config["truecolor"] else YELLOW
ORANGE = (245, 164, 66) if config["truecolor"] else YELLOW
IONIZATION_ENERGY_COL = (119, 50, 168) if config["truecolor"] else MAGENTA

types = {
	"Reactive nonmetal": (27, 156, 20) if config["truecolor"] else GREEN,
	"Noble gas": (252, 233, 61) if config["truecolor"] else YELLOW,
	"Alkali metal": (176, 176, 176) if config["truecolor"] else DEFAULT_COLOR
}

# Other important functions / variables

def save_config():
    global config_file, config
    with open(config_file, 'w', encoding="utf-8") as file:
        json.dump(config, file, indent=4)

def celcius_to_kelvin(celsius):
	return (celsius * 1e16 + 273.15 * 1e16) / 1e16

def celcius_to_fahrenheit(celsius):
	return (celsius * 1e16 * 9/5) / 1e16

def eV_to_kJpermol(eV):
    return eV * 96.485

def print_header(title):
    dashes = "-" * (width - len(title) - 2)
    print(f"--{bold(title)}{dashes}")

def print_separator():
    print()
    print("-" * width)
    print()

def convert_superscript_number(string: str) -> str:
    superscript_map = {
        "0": "⁰",
        "1": "¹",
        "2": "²",
        "3": "³",
        "4": "⁴",
        "5": "⁵",
        "6": "⁶",
        "7": "⁷",
        "8": "⁸",
        "9": "⁹",
    }
    return "".join(superscript_map.get(ch, ch) for ch in string)

def remove_superscript_number(superscript: str) -> str:
    normal_map = {
        "⁰": "0",
        "¹": "1",
        "²": "2",
        "³": "3",
        "⁴": "4",
        "⁵": "5",
        "⁶": "6",
        "⁷": "7",
        "⁸": "8",
        "⁹": "9",
    }
    return "".join(normal_map.get(ch, ch) for ch in superscript)

def conjunction_join(entries: list) -> str:
    if not entries:
        return ""
    if len(entries) == 1:
        return entries[0]
    if len(entries) == 2:
        return f"{entries[0]} and {entries[1]}"
    return f"{', '.join(entries[:-1])}, and {entries[-1]}"

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

def italic(string) -> str:
    return f"\033[3m{string}\033[23m"

def bold(string) -> str:
    return f"\033[1m{string}\033[22m"

def underline(string) -> str:
    return f"\033[4m{string}\033[24m"

def crossout(string) -> str:
    return f"\033[9m{string}\033[29m"

def blink(string) -> str:
    return f"\033[5m{string}\033[25m"

def inverse_color(string) -> str:
    return f"\033[7m{string}\033[27m"

def dim(string) -> str:
    return f"\033[2m{string}\033[22m"

tip = "(Tip: You can give this program argv to directly search an element from there. You can even give argv to the ./periodica.sh file too!)" if random.randint(0, 1) else "(Tip: run this script with the --info flag, and see what happens.)"

program_information = f"""
Welcome to {gradient("periodica", (156, 140, 255), (140, 255, 245)) if config['truecolor'] else fore("periodica", BLUE)}!
This program provides useful information about the periodic elements.
This project started as a fun hobby at around {bold("March 2025")}, but ended up getting taken seriously.
This program was built with {fore("Python", BLUE)}, and uses {fore("JSON", YELLOW)} for configuration files.
The vibrant colors and visuals were done with the help of {italic(bold("ANSI escape codes"))}, although you should note that {bold("some terminals may not have truecolor support.")}
{dim("(You can disable this anytime in the config.json file, or using the --init flag.)")}
{italic(bold(f"Special thanks to Discord user {fore("text_text_keke", CYAN)} for helping test this application!"))}
There are also other flags you can provide to this program.

- {bold("--info")} - Give this information message

Anyways, I hope you enjoy this small program. {bold("Please read the README.md file for more information!")}
"""
# Reading json file, and trying to get from GitHub if fails

elementdata_malformed = False
try:
    with open("./elementdata.json", 'r', encoding="utf-8") as file:
        data = json.load(file)
        logging.info("elementdata.json file was successfully found.")
except json.JSONDecodeError:
    logging.error("elementdata.json file was modified, please do not do so no matter what.")
    print("The elementdata.json file was modified and malformed. Please do not do so, no matter what.\nThis means you need a fresh new elementdata.json file, is it okay for me to get the file for you on GitHub? (y/n)")
    elementdata_malformed = True
except FileNotFoundError:
    logging.warning("elementdata.json file was not found.")
    print("The elementdata.json file was not found. Is it okay for me to get the file for you on GitHub? (y/n)")
    elementdata_malformed = True

if elementdata_malformed:
    confirmation = input("> ").strip().lower()
    try:
        import requests
    except ImportError:
        print("Whoopsies, the requests module was not found in your environment! Please read the README.md file for more information.")
        logging.error("Couldn't proceed; the requests library was not found in the environment.")
        time.sleep(5)
        logging.fatal("Program terminated.")
        sys.exit(1)
    if confirmation == "y":
        print("Getting content from https://raw.githubusercontent.com/Lanzoor/periodictable/main/src/elementdata.json, this should not take a while...")
        url = "https://raw.githubusercontent.com/Lanzoor/periodictable/main/src/elementdata.json"
        try:
            response = requests.get(url)
        except requests.exceptions.ConnectionError:
            print("Whoops! There was a network connection error. Please check your network connection, and try again later.")
            logging.error("Couldn't proceed; failed to connect to page.")
            time.sleep(2)
            logging.fatal("Program terminated.")
            sys.exit(1)
        if response.status_code == 200:
            print(f"HTTP status code: {response.status_code} (pass)")
            data = json.loads(response.text)
            with open("./elementdata.json", "w", encoding="utf-8") as f:
                f.write(response.text)
            print("Going back to the program, since all issues were resolved.")
            logging.info("Successfully got the elementdata.json file from https://raw.githubusercontent.com/Lanzoor/periodictable/main/src/elementdata.json.")
        else:
            print(f"Failed to download data! HTTP status code: {response.status_code}")
            logging.error(f"Failed to fetch data. Status code: {response.status_code}.")
            time.sleep(2)
            logging.fatal("Program terminated.")
            sys.exit(1)
    elif confirmation == "n":
        print("Okay, exiting...")
        logging.error("User denied confirmation for fetching the elementdata.json file.")
        time.sleep(2)
        logging.fatal("Program terminated.")
        sys.exit(1)
    else:
        print("Invalid input, please try again later. Exiting...")
        logging.error("User gave invalid confirmation.")
        time.sleep(2)
        logging.fatal("Program terminated.")
        sys.exit(1)

# Getting element / isotope

width = os.get_terminal_size().columns

if width <= 80:
    print(fore(f"You are running this program in a terminal that has a width of {bold(width)},\nwhich may be too compact to display and provide the information.\nPlease try resizing your terminal.", RED))
    logging.warning("Not enough width for terminal.")

element = None

def match_isotope_input(input_str):
    if isotope_match := re.match(r"^(\d+)([A-Za-z]+)$", input_str):  # 1H
        return isotope_match.group(2), isotope_match.group(1)
    if isotope_match := re.match(r"^([A-Za-z]+)[\s\-]*(\d+)$", input_str):  # H-1 or Hydrogen-1
        return isotope_match.group(1), isotope_match.group(2)
    return None, None

def format_isotope(norm_iso, fullname):
    format_style = config.get("isotope_format", "symbol-number").lower()

    match = re.match(r"^(\d+)\s*([A-Za-z]+)$", remove_superscript_number(norm_iso))
    if not match:
        return norm_iso
    else:
        number, symbol = match.groups()
        symbol = symbol.capitalize()

        if format_style == "fullname-number":
            return f"{fullname.capitalize()}-{number}"
        elif format_style == "numbersymbol":
            return f"{convert_superscript_number(str(number)) if config['use_superscript'] else number}{symbol}"
        else:
            return f"{symbol}-{number}"

def print_isotope(norm_iso, info, fullname):
    print()
    format_style = config.get("isotope_format", "symbol-number").lower()
    match = re.match(r"^(\d+)\s*([A-Za-z]+)$", remove_superscript_number(norm_iso))

    if not match:
        display_name = norm_iso
    else:
        display_name = format_isotope(norm_iso, fullname)

    if 'name' in info:
        print(f"- {bold(display_name)} ({bold(info['name'])}):")
    else:
        print(f"- {bold(display_name)}:")

    protons = info['protons']
    neutrons = info['neutrons']
    electrons = info['electrons']
    up_quarks = (info['protons'] * 2) + info['neutrons']
    down_quarks = info['protons'] + (info['neutrons'] * 2)
    half_life = info['half_life']
    isotope_weight = info['isotope_weight']

    print(f"   p⁺ - {fore("Protons", RED)}: {bold(protons)}")
    print(f"   n⁰ - {fore("Neutrons", BLUE)}: {bold(neutrons)}")
    print(f"   e⁻ - {fore("Electrons", YELLOW)}: {bold(electrons)}")
    print(f"   u - {fore("Up Quarks", UP_QUARKS_COL)}: {bold(up_quarks)} (({fore(protons, RED)} * 2) + {fore(neutrons, BLUE)} = {bold(up_quarks)})")
    print(f"   d - {fore("Down Quarks", DOWN_QUARKS_COL)}: {bold(down_quarks)} ({fore(protons, RED)} + ({fore(neutrons, BLUE)} * 2) = {bold(down_quarks)})")

    print(f"   t1/2 - Half Life: {bold(half_life) if half_life is not None else fore('Stable', NULL_COL)}")
    print(f"   u - Isotope Weight: {bold(isotope_weight)}g/mol")

    if 'daughter_isotope' in info:
        print(f"   🪞 - Daughter Isotope: {bold(format_isotope(info['daughter_isotope'], fullname))}")
    if 'decay' in info:
        print(f"   ⛓️ - Decay Mode: {bold(info['decay'])}")

def find_isotope(symbol_or_name, mass_number, search_query):
    for val in data.values():
        sym = val["general"]["symbol"].lower()
        name = val["general"]["fullname"].lower()
        if symbol_or_name.lower() in (sym, name):
            for isotope, info in val["nuclear"]["isotopes"].items():
                norm_iso_match = re.match(r"^(.*?)(?:\s*-\s*.*)?$", isotope)
                norm_iso = norm_iso_match.group(1) if norm_iso_match else isotope
                if (remove_superscript_number(norm_iso).lower() == f"{mass_number}{sym}" or
                    remove_superscript_number(norm_iso).lower() == f"{sym}{mass_number}" or
                    norm_iso.lower() == search_query):
                    logging.info(f"Found isotope match: {mass_number}{sym.capitalize()} / {name.capitalize()}")
                    print_separator()
                    print_isotope(norm_iso, info, name)
                    print_separator()
                    return True
    return False

def find_element(input_str):
    input_str = input_str.lower()
    possible_names = []
    for val in data.values():
        name = val["general"]["fullname"].lower()
        symbol = val["general"]["symbol"].lower()
        possible_names.extend([name, symbol])

        if input_str == name:
            logging.info(f"Matched element full name: {input_str.capitalize()}")
            return val, None
        elif input_str == symbol:
            logging.info(f"Matched element symbol: {input_str.capitalize()} ({val['general']['fullname']})")
            return val, None

    suggestion = difflib.get_close_matches(input_str, possible_names, n=1, cutoff=0.6)
    return None, suggestion

element = None
suggestion = None

if len(sys.argv) > 1:
    if "--info" in sys.argv:
        print(program_information)
        sys.exit(0)
    elif "--init" in sys.argv:
        sys.exit(0)
    input_str = sys.argv[1].strip().lower()
    logging.info(f"User gave argv: \"{input_str}\"")

    try:
        index = int(input_str) - 1
        key = list(data.keys())[index]
        element = data[key]
    except (ValueError, IndexError):
        symbol_or_name, mass_number = match_isotope_input(input_str)

        if symbol_or_name and mass_number:
            found = find_isotope(symbol_or_name, mass_number, input_str)
            if found:
                sys.exit(0)
            logging.warning(f"Invalid isotope input: {input_str}")
        else:
            element, suggestion = find_element(input_str)

    if element is None:
        if not suggestion:
            print(fore("Invalid argv; falling back to interactive input.", RED))
        else:
            print(fore(f"Invalid argv. Did you mean \"{bold(suggestion[0])}\"?", YELLOW))
        logging.warning("Argv invalid, fallback to interactive.")

else:
    logging.warning("Argument not given, falling back to interactive input.")

if element is None:
    print(f"Search for an element by name, symbol, or atomic number. {dim(tip)}")
    while True:
        input_str = input("> ").strip().lower()
        logging.info(f"User gave input: \"{input_str}\"")

        suggestion = None

        try:
            index = int(input_str) - 1
            key = list(data.keys())[index]
            element = data[key]
        except (ValueError, IndexError):
            symbol_or_name, mass_number = match_isotope_input(input_str)

            if symbol_or_name and mass_number:
                found = find_isotope(symbol_or_name, mass_number, input_str)
                if found:
                    sys.exit(0)
                logging.warning(f"Invalid isotope input: {input_str}")
            else:
                element, suggestion = find_element(input_str)

        if element is not None:
            break

        if not suggestion:
            print("Not a valid element or isotope, please try again.")
        else:
            print(fore(f"Not a valid element or isotope. Did you mean \"{bold(suggestion[0])}\"?", YELLOW))

# General info
fullname = element["general"]["fullname"]
symbol = element["general"]["symbol"]
atomic_number = element["general"]["atomic_number"]
description = element["general"]["description"]
discoverers = element["historical"]["discoverers"]
discovery_date = element["historical"]["date"]
period = element["general"]["period"]
group = element["general"]["group"]
element_type = element["general"]["type"]
block = element["general"]["block"]
cas_number = element["general"]["cas_number"]

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

if atomic_number in range(57, 72):
    lanthanides[atomic_number - 57 + 3] = fore("▪", GREEN)
elif atomic_number in range(89, 104):
    actinides[atomic_number - 89 + 3] = fore("▪", GREEN)
else:
    periodic_table[period - 1][group - 1] = fore("▪", GREEN)

entries = [
    bold(fore(name, MALE if gender == "male" else FEMALE))
    for name, gender in discoverers.items()
]

discoverers = conjunction_join(entries)

# Nuclear properties
protons = element["nuclear"]["protons"]
neutrons = element["nuclear"]["neutrons"]
electrons = element["nuclear"]["electrons"]
valence_electrons = element["nuclear"]["valence_electrons"]
up_quarks = (protons * 2) + neutrons
down_quarks = protons + (neutrons * 2)
shells = element["electronic"]["shells"]
subshells = element["electronic"]["subshells"]
isotopes = element["nuclear"]["isotopes"]

possible_shells = "klmnopqrstuvwxyz"
shell_result = ""
for index, electron in enumerate(shells):
    max_capacity = ((index + 1) ** 2) * 2
    if index != len(shells) - 1:
        shell_result += f"{bold(str(electron) + str(possible_shells[index]))} ({electron}/{max_capacity}), "
    else:
        shell_result += f"{bold(fore(electron, VALENCE_ELECTRONS_COL) + fore(possible_shells[index], VALENCE_ELECTRONS_COL))} ({electron}/{max_capacity})"

subshell_capacities = {'s': 2, 'p': 6, 'd': 10, 'f': 14}
subshell_result = ""
for subshell in subshells:
    subshell = remove_superscript_number(subshell) if not config["use_superscript"] else subshell
    match = re.match(r"(\d)([spdf])(\d+)", subshell)
    if match:
        _, subshell_type, electron_count = match.groups()
        max_capacity = subshell_capacities[subshell_type]
        subshell_result += f"{bold(subshell)} ({electron_count}/{max_capacity}), "
    else:
        subshell_result += f"{bold(subshell)}, "

subshell_result = subshell_result.rstrip(", ")

# Physical properties
melting_point = element["physical"]["melt"]
boiling_point = element["physical"]["boil"]
atomic_mass = element["physical"]["atomic_mass"]
radioactive = element["general"]["radioactive"]
half_life = element["general"]["half_life"]
density = element["physical"]["density"]

# Electronic properties
electronegativity = element["electronic"]["electronegativity"]
electron_affinity = element["electronic"]["electron_affinity"]
ionization_energy = element["electronic"]["ionization_energy"]
oxidation_states = element["electronic"]["oxidation_states"]

negatives: list = [0, -1, -2, -3, -4, -5]
positives: list = [1, 2, 3, 4, 5, 6, 7, 8, 9]

for index, neg_state in enumerate(negatives):
    if neg_state in oxidation_states:
        if neg_state == 0:
            negatives[index] = bold(fore(neg_state, GREEN))
        elif neg_state < 0:
            negatives[index] = bold(fore(neg_state, BLUE))
        else:
            negatives[index] = bold(fore(neg_state, RED))
    else:
        negatives[index] = dim(neg_state)

for index, pos_state in enumerate(positives):
    if pos_state in oxidation_states:
        if pos_state == 0:
            positives[index] = bold(fore(pos_state, GREEN))
        elif pos_state < 0:
            positives[index] = bold(fore(pos_state, BLUE))
        else:
            positives[index] = bold(fore(pos_state, RED))
    else:
        positives[index] = dim(pos_state)

negatives = ", ".join(negatives)
positives = ", ".join(positives)

conductivity_type = element["electronic"]["conductivity_type"]

# Measurements
radius = element["measurements"]["radius"]
hardness = element["measurements"]["hardness"]
atomic_volume = element["measurements"]["atomic_volume"]
sound_transmission_speed = element["measurements"]["sound_transmission_speed"]

logging.info("Starting output.")

print()
print_header("General")
print()

print(f" 🔡 - Element Name: {bold(fullname)} ({bold(symbol)})")
print(f" Z - Atomic Number: {bold(atomic_number)}")
print(f" 📃 - Description:\n\n    {description}\n")
print(f" 🔍 - Discoverer(s): {discoverers}")
print(f" 🔍 - Discovery Date: {bold(discovery_date)}")
print(f" ↔️ - Period (Row): {bold(period)}")
print(f" ↕️ - Group (Column): {bold(group)}")
print(f" 🎨 - Type: {fore(element_type, types[element_type])}")
print(f" 🧱 - Block: {bold(block)}")
print(f" 📇 - CAS Number: {bold(cas_number)}")

print()

print("  ", end="")
for y in periodic_table:
    for x in y:
        print(x, end=" ")
    print("\n  ", end="")

print()

for lanth in lanthanides:
    print(lanth, end=" ")

print()

for actin in actinides:
    print(actin, end=" ")

print()

print()
print_header("Nuclear Properties")
print()

print(f" p⁺ - {fore("Protons", RED)}: {bold(protons)}")
print(f" n⁰ - {fore("Neutrons", BLUE)}: {bold(neutrons)}")
print(f" e⁻ - {fore("Electrons", YELLOW)}: {bold(electrons)}")
print(f" nv - {fore("Valence Electrons", VALENCE_ELECTRONS_COL)}: {bold(valence_electrons)}")
print(f" u - {fore("Up Quarks", UP_QUARKS_COL)}: {bold(up_quarks)} (({fore(protons, RED)} * 2) + {fore(neutrons, BLUE)} = {bold(up_quarks)})")
print(f" d - {fore("Down Quarks", DOWN_QUARKS_COL)}: {bold(down_quarks)} ({fore(protons, RED)} + ({fore(neutrons, BLUE)} * 2) = {bold(down_quarks)})")
print(f" ⚛️ - Shells {dim(f"(The electron in {fore("yellow", VALENCE_ELECTRONS_COL)} is the valence electron)")}:\n    {shell_result}")
print(f" 🌀 - Subshells: {subshell_result}")
print(" 🪞 - Isotopes:")

for isotope, information in isotopes.items():
    print_isotope(isotope, information, fullname)

print()
print_header("Physical Properties")
print()

print(f" 💧 - {fore("Melting Point", MELT_COL)}: {bold(melting_point)}°C = {bold(celcius_to_fahrenheit(melting_point))}°F = {bold(celcius_to_kelvin(melting_point))}K")
print(f" 💨 - {fore("Boiling Point", BOIL_COL)}: {bold(boiling_point)}°C = {bold(celcius_to_fahrenheit(boiling_point))}°F = {bold(celcius_to_kelvin(boiling_point))}K")
print(f" A - Mass Number: {fore(protons, RED)} + {fore(neutrons, BLUE)} = {bold(protons + neutrons)}")
print(f" u - Atomic Mass: {bold(atomic_mass)}g/mol")
print(f" ☢️ - {fore("Radioactive", ORANGE)}: {fore("Yes", GREEN) if radioactive else fore("No", RED)}")
print(f" t1/2 - Half Life: {bold(half_life if not (half_life is None) else fore("Stable", NULL_COL))}")
print(f" ρ - Density: {bold(density)}g/cm³")

print()
print_header("Electronic Properties")
print()

print(f" χ - Electronegativity: {bold(electronegativity)}")
print(f" EA - Electron Affinity: {bold(electron_affinity)}eV = {bold(eV_to_kJpermol(electron_affinity))}kJ/mol")
print(f" IE - {fore("Ionization Energy", IONIZATION_ENERGY_COL)}: {bold(ionization_energy)}eV = {bold(eV_to_kJpermol(ionization_energy))}kJ/mol")
print(f" ⚡️ - {fore("Oxidation States", YELLOW)} {dim(f"(Only the ones that have {fore("color", BLUE)} are activated)")}:\n{"   " + negatives}\n{"   " + positives}\n")
print(f" ⚡️ - Conductivity Type: {bold(conductivity_type)}")

print()
print_header("Measurements")
print()

print(" 📏 - Radius: ")
print(f"   r_calc - Calculated: {bold(str(radius["calculated"]) + "pm" if not (radius["calculated"] is None) else fore("N/A", NULL_COL))}")
print(f"   r_emp - Empirical: {bold(str(radius["empirical"]) + "pm" if not (radius["empirical"] is None) else fore("N/A", NULL_COL))}")
print(f"   r_cov - Covalent: {bold(str(radius["covalent"]) + "pm" if not (radius["covalent"] is None) else fore("N/A", NULL_COL))}")
print(f"   rvdW - Van der Waals: {bold(str(radius["van_der_waals"]) + "pm" if not (radius["van_der_waals"] is None) else fore("N/A", NULL_COL))}\n")
print(" 🪨 - Hardness: ")
print(f"   HB - Brinell: {bold(str(hardness["brinell"]) + " kgf/mm²" if not (hardness["brinell"] is None) else fore("None", NULL_COL))}")
print(f"   H - Mohs: {bold(str(hardness["mohs"]) if not (hardness["mohs"] is None) else fore("None", NULL_COL))}")
print(f"   HV - Vickers: {bold(str(hardness["vickers"]) + " kgf/mm²" if not (hardness["vickers"] is None) else fore("None", NULL_COL))}\n")
print(f" Va - Atomic Volume: ≈ {bold(atomic_volume)}cm³/mol")
print(f" 📢 - Speed of Sound Transmission: {bold(sound_transmission_speed)}m/s = {bold(sound_transmission_speed / 1000)}km/s")

print_separator()