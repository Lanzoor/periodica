import logging, json

with open('./execution.log', 'w'):
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
    "truecolor": True
}

try:
    with open('./config.json', 'r') as file:
        config = json.load(file)
        logging.info("The configuration file was found.")
except json.JSONDecodeError:
    with open('./config.json', 'w') as file:
        config = default_options
        file.write(json.dumps(default_options))
        logging.info("Overwrited configuration file since it was malformed.")
except FileNotFoundError:
    with open('./config.json', 'w') as file:
        config = default_options
        file.write(json.dumps(default_options))
        logging.info("Created a new configuration file, since it didn't exist.")

for key, value in default_options.items():
    config.setdefault(key, value)

# Color Configs

PROTONS_COL = (255, 56, 56)
NEUTRONS_COL = (38, 72, 209)
ELECTRONS_COL = (255, 237, 122)
VALENCE_ELECTRONS_COL = (255, 241, 163)
UP_QUARKS_COL = (122, 255, 129)
DOWN_QUARKS_COL = (230, 156, 60)
MALE = (109, 214, 237)
FEMALE = (255, 133, 245)
NULL_COL = (90, 232, 227)
MELT_COL = (52, 110, 235)
BOIL_COL = (189, 165, 117)
OXIDATION_STATES_COL = (66, 50, 168)
IONIZATION_ENERGY_COL = (119, 50, 168)

BLACK = 0
RED = 1
GREEN = 2
YELLOW = 3
BLUE = 4
MAGENTA = 5
CYAN = 6
WHITE = 7
DEFAULT_COLOR = 9

types = {
	"Reactive nonmetal": (27, 156, 20),
	"Noble gas": (114, 54, 209),
	"Alkali metal": (176, 176, 176)
}

# Other important functions / variables

import colorsys, random

def save_config():
    global config_file, config
    with open(config_file, 'w') as file:
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

def remove_superscript_number(superscript: str) -> str:
    res = superscript.replace("¹", "1").replace("²", "2").replace("³", "3").replace("⁴", "4").replace("⁵", "5").replace("⁶", "6").replace("⁷", "7").replace("⁸", "8").replace("⁹", "9").replace("⁰", "0")
    return res

def fore(string, color: int, *, bright: bool = False) -> str:
    processed = str(string)
    if color > 7 and color != 9: raise Exception("Unsupported default terminal color.")
    try:
        return f"\033[{(30 + color) if not bright else (90 + color)}m{processed}\033[39m"
    except ValueError:
        raise Exception("Unsupported default terminal color.")

def back(string, color: int, *, bright: bool = False) -> str:
    processed = str(string)
    if color > 7 and color != 9: raise Exception("Unsupported default terminal color.")
    try:
        return f"\033[{(40 + color) if not bright else (100 + color)}m{processed}\033[49m"
    except ValueError:
        raise Exception("Unsupported default terminal color.")

def custom_fore(string, rgb: list[int] | tuple[int, int, int]) -> str:
    processed = str(string)
    r, g, b = rgb
    return f"\033[38;2;{r};{g};{b}m{processed}\033[39m"

def custom_back(string, rgb: list[int] | tuple[int, int, int]) -> str:
    processed = str(string)
    r, g, b = rgb
    return f"\033[48;2;{r};{g};{b}m{processed}\033[49m"

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
        res[index] = custom_fore(char, (new_r, new_g, new_b))
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

tip = "(Tip: You can give this program argv to directly search an element from there. You can even give argv to the ./periodica.sh file too!)" if random.randint(0, 1) else ""

# Reading json file, and trying to get from GitHub if fails

import re, sys, time

elementdata_malformed = False
try:
    with open("./elementdata.json", 'r') as file:
        data = json.loads(file)
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
            with open("./elementdata.json", "w") as f:
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


import os, re

width = os.get_terminal_size().columns

if width <= 80:
    print(fore(f"You are running this program in a terminal that has a width of {bold(width)},\nwhich may be too compact to display and provide the information.\nPlease try resizing your terminal.", RED))
    logging.warning("Not enough width for terminal.")

element = None

if len(sys.argv) > 1:
    search_query = sys.argv[1].strip().lower()
    logging.info(f"User gave argv: \"{search_query}\"")
    try:
        idx = int(search_query) - 1
        key = list(data.keys())[idx]
        element = data[key]
        logging.info(f"User gave an atomic number {idx}, proceeding...")
    except (ValueError, IndexError):
        isotope_match = re.match(r"(\d+)([A-Za-z]+)", search_query)
        if isotope_match:
            number, symbol = isotope_match.groups()
            found_isotope = False
            for val in data.values():
                if val["general"]["symbol"].lower() == symbol.lower():
                    for isotope, info in val["nuclear"]["isotopes"].items():
                        norm_iso_match = re.match(r"^(.*?)(?:\s*-\s*.*)?$", isotope)
                        norm_isotope = norm_iso_match.group(1) if norm_iso_match else isotope
                        if norm_isotope.lower() == search_query or remove_superscript_number(norm_isotope.lower()) == search_query:
                            logging.info(f"User gave isotope {number}{symbol.capitalize()} with number {number} and symbol {symbol.capitalize()}.")
                            print()
                            print(bold(norm_isotope) if config["use_superscript"] else bold(remove_superscript_number(norm_isotope)) + ":")
                            print(f"   t1/2 - Half Life: {bold(info['half_life']) if info['half_life'] is not None else custom_fore('None', NULL_COL)}")
                            print(f"   u - Isotope Weight: {bold(info['isotope_weight'])}g/mol")
                            if 'daughter_isotope' in info:
                                print(f"   🪞 - Daughter Isotope: {bold(info['daughter_isotope'])}")
                            if 'decay' in info:
                                print(f"   ⛓️‍💥 - Decay Mode: {bold(info['decay'])}")
                            print()
                            sys.exit(0)
            print(fore("Invalid argv; falling back to interactive input.", RED))
            logging.warning(f"User gave invalid isotope {search_query.capitalize()}, fallback to interactive.")
            element = None
        else:
            for val in data.values():
                if search_query == val["general"]["fullname"].lower():
                    element = val
                    logging.info(f"User gave element full name: {search_query.capitalize()}.")
                    break
                elif search_query == val["general"]["symbol"].lower():
                    element = val
                    logging.info(f"User gave element symbol: {search_query.capitalize()} for {element['general']['fullname']}.")
                    break
            if element is None:
                print(fore("Invalid argv; falling back to interactive input.", RED))
                logging.warning("Argv invalid, falling back to interactive input.")
else:
    logging.warning("Argument not given, falling back to interactive input.")

if element is None:
    print(f"Search for an element by name, symbol, or atomic number. {dim(tip)}")
    while True:
        user_input = input("> ").strip().lower()
        logging.info(f"User gave input: \"{user_input}\"")
        try:
            idx = int(user_input) - 1
            key = list(data.keys())[idx]
            element = data[key]
            logging.info(f"User gave atomic number {idx}, proceeding...")
            break
        except (ValueError, IndexError):
            isotope_match = re.match(r"(\d+)([A-Za-z]+)", user_input)
            if isotope_match:
                number, symbol = isotope_match.groups()
                found_isotope = False
                for val in data.values():
                    if val["general"]["symbol"].lower() == symbol.lower():
                        for isotope, info in val["nuclear"]["isotopes"].items():
                            norm_iso_match = re.match(r"^(.*?)(?:\s*-\s*.*)?$", isotope)
                            norm_isotope = norm_iso_match.group(1) if norm_iso_match else isotope
                            if norm_isotope.lower() == user_input or remove_superscript_number(norm_isotope.lower()) == user_input:
                                logging.info(f"User gave isotope {number}{symbol.capitalize()} with number {number} and symbol {symbol.capitalize()}.")
                                print()
                                print(bold(norm_isotope) if config["use_superscript"] else bold(remove_superscript_number(norm_isotope)) + ":")
                                print(f"   t1/2 - Half Life: {bold(info['half_life']) if info['half_life'] is not None else custom_fore('None', NULL_COL)}")
                                print(f"   u - Isotope Weight: {bold(info['isotope_weight'])}g/mol")
                                if 'daughter_isotope' in info:
                                    print(f"   🪞 - Daughter Isotope: {bold(info['daughter_isotope'])}")
                                if 'decay' in info:
                                    print(f"   ⛓️‍💥 - Decay Mode: {bold(info['decay'])}")
                                print()
                                sys.exit(0)
                logging.warning(f"User gave invalid isotope {number}{symbol.capitalize()}, trying again.")
                continue

            for val in data.values():
                if user_input == val["general"]["fullname"].lower():
                    element = val
                    logging.info(f"User gave element full name: {user_input.capitalize()} for {element['general']['fullname']}.")
                    break
                elif user_input == val["general"]["symbol"].lower():
                    element = val
                    logging.info(f"User gave element symbol: {user_input.capitalize()}.")
                    break
            if element:
                break

        print("Not a valid element. Try again.")
        logging.info(f"User input \"{user_input}\" was invalid, trying again.")

# General info
fullname = element["general"]["fullname"]
symbol = element["general"]["symbol"]
atomic_number = element["general"]["atomic_number"]
description = element["general"]["description"]
discoverers = element["historical"]["discoverers"]
discovery_year = element["historical"]["year"]
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

discoverers_result = ""
era = "AD" if discovery_year > 0 else "BC"

discoverers_result = ""
era = "AD" if discovery_year > 0 else "BC"

for name, gender in discoverers.items():
    if list(discoverers.keys()).index(name) != len(list(discoverers.keys())) -1:
        discoverers_result += f"{custom_fore(name, MALE if gender == "male" else FEMALE)}, "
    else:
        discoverers_result += f"{custom_fore(name, MALE if gender == "male" else FEMALE)}"

# Nuclear properties
protons = element["nuclear"]["protons"]
neutrons = element["nuclear"]["neutrons"]
electrons = element["nuclear"]["electrons"]
valence_electrons = element["nuclear"]["valence_electrons"]
up_quarks = element["nuclear"]["quarks"]["up"]
down_quarks = element["nuclear"]["quarks"]["down"]
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
        shell_result += f"{bold(custom_fore(electron, VALENCE_ELECTRONS_COL) + custom_fore(possible_shells[index], VALENCE_ELECTRONS_COL))} ({electron}/{max_capacity})"

subshell_capacities = {'s': 2, 'p': 6, 'd': 10, 'f': 14}
subshell_result = ""
for subshell in subshells:
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

print(f" 🔡 - Element Name: {bold(fullname)} ({bold(symbol)})")
print(f" Z - Atomic Number: {bold(atomic_number)}")
print(f" 📃 - Description:\n\n    {description}\n")
print(f" 🔍 - Discoverer(s): {discoverers_result}")
print(f" 🔍 - Discovery Date: {abs(discovery_year)} {era}")
print(f" ↔️ - Period (Row): {bold(period)}")
print(f" ↕️ - Group (Column): {bold(group)}")
print(f" 🎨 - Type: {custom_fore(element_type, types[element_type])}")
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

print(f" p⁺ - {custom_fore("Protons", PROTONS_COL)}: {bold(protons)}")
print(f" n⁰ - {custom_fore("Neutrons", NEUTRONS_COL)}: {bold(neutrons)}")
print(f" e⁻ - {custom_fore("Electrons", ELECTRONS_COL)}: {bold(electrons)}")
print(f" nv - {custom_fore("Valence Electrons", VALENCE_ELECTRONS_COL)}: {bold(valence_electrons)}")
print(f" u - {custom_fore("Up Quarks", UP_QUARKS_COL)}: {bold(up_quarks)} (({custom_fore(protons, PROTONS_COL)} * 2) + {custom_fore(neutrons, NEUTRONS_COL)} = {bold(up_quarks)})")
print(f" d - {custom_fore("Down Quarks", DOWN_QUARKS_COL)}: {bold(down_quarks)} ({custom_fore(protons, PROTONS_COL)} + ({custom_fore(neutrons, NEUTRONS_COL)} * 2) = {bold(down_quarks)})")
print(f" ⚛️ - Shells {dim(f"(The electron in {custom_fore("yellow", VALENCE_ELECTRONS_COL)} is the valence electron)")}:\n    {shell_result}")
print(f" 🌀 - Subshells: {subshell_result}")
print(" 🪞 - Isotopes:\n")

for isotope, information in isotopes.items():
    print(" - " + bold(isotope) if config["use_superscript"] else bold(remove_superscript_number(isotope)) + ":")
    print(f"   t1/2 - Half Life: {bold(information["half_life"]) if not (information["half_life"] is None) else custom_fore("None", NULL_COL)}")
    print(f"   u - Isotope Weight: {bold(information["isotope_weight"])}g/mol")
    try:
        print(f"   🪞 - Daughter Isotope: {bold(information["daughter_isotope"])}")
    except KeyError:
        pass

    try:
        print(f"   ⛓️‍💥 - Decay Mode: {bold(information["decay"])}")
    except KeyError:
        pass
    print()

print_header("Physical Properties")

print(f" 💧 - {custom_fore("Melting Point", MELT_COL)}: {bold(melting_point)}°C = {bold(celcius_to_fahrenheit(melting_point))}°F = {bold(celcius_to_kelvin(melting_point))}K")
print(f" 💨 - {custom_fore("Boiling Point", BOIL_COL)}: {bold(boiling_point)}°C = {bold(celcius_to_fahrenheit(boiling_point))}°F = {bold(celcius_to_kelvin(boiling_point))}K")
print(f" A - Mass Number: {custom_fore(protons, PROTONS_COL)} + {custom_fore(neutrons, NEUTRONS_COL)} = {bold(protons + neutrons)}")
print(f" u - Atomic Mass: {bold(atomic_mass)}g/mol")
print(f" ☢️ - Radioactive: {fore("Yes", GREEN) if radioactive else fore("No", RED)}")
print(f" t1/2 - Half Life: {bold(half_life) if not (half_life is None) else custom_fore("None", NULL_COL)}")
print(f" ρ - Density: {bold(density)}g/cm³")

print()
print_header("Electronic Properties")

print(f" χ - Electronegativity: {bold(electronegativity)}")
print(f" EA - Electron Affinity: {bold(electron_affinity)}eV = {bold(eV_to_kJpermol(electron_affinity))}kJ/mol")
print(f" IE - {custom_fore("Ionization Energy", IONIZATION_ENERGY_COL)}: {bold(ionization_energy)}eV = {bold(eV_to_kJpermol(ionization_energy))}kJ/mol")
print(f" ⚡️ - {custom_fore("Oxidation States", OXIDATION_STATES_COL)} {dim(f"(Only the ones that have {gradient("color", (50, 151, 168), (59, 38, 191))} are activated)")}:\n{"   " + negatives}\n{"   " + positives}\n")
print(f" ⚡️ - Conductivity Type: {bold(conductivity_type)}")

print()
print_header("Measurements")

print(" 📏 - Radius: ")
print(f"   r_calc - Calculated: {bold(str(radius["calculated"]) + "pm" if not (radius["calculated"] is None) else custom_fore("N/A", NULL_COL))}")
print(f"   r_emp - Empirical: {bold(str(radius["empirical"]) + "pm" if not (radius["empirical"] is None) else custom_fore("N/A", NULL_COL))}")
print(f"   r_cov - Covalent: {bold(str(radius["covalent"]) + "pm" if not (radius["covalent"] is None) else custom_fore("N/A", NULL_COL))}")
print(f"   rvdW - Van der Waals: {bold(str(radius["van_der_waals"]) + "pm" if not (radius["van_der_waals"] is None) else custom_fore("N/A", NULL_COL))}\n")
print(" 🪨 - Hardness: ")
print(f"   HB - Brinell: {bold(str(hardness["brinell"]) + " kgf/mm²" if not (hardness["brinell"] is None) else custom_fore("None", NULL_COL))}")
print(f"   H - Mohs: {bold(str(hardness["mohs"]) if not (hardness["mohs"] is None) else custom_fore("None", NULL_COL))}")
print(f"   HV - Vickers: {bold(str(hardness["vickers"]) + " kgf/mm²" if not (hardness["vickers"] is None) else custom_fore("None", NULL_COL))}\n")
print(f" Va - Atomic Volume: ≈ {bold(atomic_volume)}cm³/mol")
print(f" 📢 - Speed of Sound Transmission: {bold(sound_transmission_speed)}m/s = {bold(sound_transmission_speed / 1000)}km/s")
print()
