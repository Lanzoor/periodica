#!/usr/bin/env python3

import logging, json, os, re, sys, difflib, random, typing, pathlib
from utils import get_config, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, B_BLACK, fore, bold, dim, italic, gradient, animate_print, clear_screen, abort_program, get_response

# src -> periodica, two parents
PERIODICA_DIR = pathlib.Path(__file__).resolve().parent.parent

OUTPUT_FILE = PERIODICA_DIR / "src" / "output.json"
CONFIG_FILE = PERIODICA_DIR / "src" / "config.json"
DATA_FILE = PERIODICA_DIR / "src" / "data.json"
EXPORT = False

element_data = None
element_suggestion = ""
recognized_flag = False
elementdata_malformed = False

config = get_config()

superscripts = config["use_superscripts"]
truecolor = config["truecolor"]
isotope_format = config["isotope_format"]
animation_type = config["animation"]
animation_delay = config["animation_delay"]

if truecolor:
    VALENCE_ELECTRONS_COL = (248, 255, 166)
    MALE = (109, 214, 237)
    FEMALE = (255, 133, 245)
    MELT_COL = (52, 110, 235)
    BOIL_COL = (189, 165, 117)
    ORANGE = (245, 164, 66)
    INDIGO = (94, 52, 235)
else:
    VALENCE_ELECTRONS_COL = YELLOW
    MALE = CYAN
    FEMALE = MAGENTA
    MELT_COL = BLUE
    BOIL_COL = YELLOW
    ORANGE = YELLOW
    INDIGO = BLUE

cm3 = "cm³" if superscripts else "cm3"
mm2 = "mm²" if superscripts else "mm2"
full_data = {}

types = {
	"Reactive nonmetal": GREEN,
	"Noble gas": YELLOW,
	"Alkali metal": (176, 176, 176) if truecolor else B_BLACK,
	"Alkali earth metal": ORANGE,
	"Metalloid": CYAN
}

def celcius_to_kelvin(celsius):
	return (celsius * 1e16 + 273.15 * 1e16) / 1e16

def celcius_to_fahrenheit(celsius):
	return (celsius * 9 / 5) + 32

def eV_to_kJpermol(eV):
    return eV * 96.485

def print_header(title):
    dashes = "-" * (width - len(title) - 2)
    print(f"--{bold(title)}{dashes}")

def print_separator():
    print()
    print("-" * width)
    print()

def convert_superscripts(string: str) -> str:
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
        "+": "⁺",
        "-": "⁻"
    }
    return "".join(superscript_map.get(ch, ch) for ch in string)

def remove_superscripts(superscript: str) -> str:
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
        "⁺": "+",
        "⁻": "-"
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

def create_flag(*flags: str, callable):
    for arg in sys.argv[1:]:
        if arg in flags:
            callable()
            return True
    return False

def get_information():
    logging.info("User gave --info flag; redirecting to information logic.")
    animate_print(program_information)
    sys.exit(0)

def configurate():
    logging.info("User gave --init flag; redirecting to another script.")
    import configuration
    sys.exit(0)

def check_for_update():
    logging.info("User gave --update flag; redirecting to update logic.")
    from update import update_main
    update_main()
    sys.exit(0)

def view_table():
    logging.info("User gave --table flag; redirecting to another logic.")

    COLUMNS = 18 * 4
    ROWS = 7 * 3
    if width < COLUMNS:
        animate_print(f"Well, the terminal is way too small to display the table. Please run this on a larger window.\n{bold(f"At least a terminal size of {COLUMNS} x {ROWS} is required to display the content.")}")
        abort_program("Terminal too small to display the table.")
        sys.exit(0)

    if height < ROWS:
        animate_print(f"Well, the terminal is way too small to display the table. Please run this on a larger window.\n{bold(f"At least a terminal size of {COLUMNS} x {ROWS} is required to display the content.")}")
        abort_program("Terminal too small to display the table.")
        sys.exit(0)

    clear_screen()

    # TODO: Continue the logic. Way too busy to refactor stuff for now.

    sys.exit(0)

def export():
    global EXPORT

    if "--export" not in sys.argv:
        return

    EXPORT = True
    sys.argv.remove("--export")

    args = [arg for arg in sys.argv[1:] if not arg.startswith("--")]

    if len(args) > 1:
        animate_print(fore("Invalid usage. Example usage: ./periodica.sh --export H. Please run the script with the --info flag to get information.", RED))
        abort_program("Export flag with too many arguments.")
        sys.exit(1)

    element = None
    if args:
        user_input = args[0]
        element, _ = process_isotope_input(user_input)
        if element is None:
            animate_print(fore("Could not find that element or isotope. Please enter one manually.", RED))

    animate_print(f"Search for an element {italic("to export")} by name, symbol, or atomic number.")

    while element is None:
        user_input = input("> ").strip()
        element, _ = process_isotope_input(user_input)
        if element is None:
            animate_print(fore("Could not find element or isotope to export. Please try again.", RED))

    if "info" in element and "symbol" in element:
        name = f"{element['isotope']}"
    else:
        name = f"{element['general']['fullname'].capitalize()}"

    animate_print(f"Saving data of {bold(name)} to {OUTPUT_FILE}...")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        if "info" in element and "symbol" in element:
            json.dump({
                "symbol": element["symbol"].capitalize(),
                "fullname": element["fullname"],
                "isotope": element["isotope"],
                "data": element["info"]
            }, file, indent=4, ensure_ascii=False)
        else:
            json.dump(element, file, indent=4, ensure_ascii=False)

    animate_print(fore(f"Successfully saved to {OUTPUT_FILE}.", GREEN))
    sys.exit(0)

def get_element_argument() -> str | None:
    return next((arg for arg in sys.argv[1:] if not arg.startswith("--")), None)

def match_isotope_input(user_input) -> typing.Tuple[str | None, str | None]:
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
    animate_print(f"      t1/2 - Half Life: {bold(half_life) if half_life else fore('Stable', CYAN)}")
    animate_print(f"      u - Isotope Weight: {bold(info['isotope_weight'])}g/mol")

    def show_decay(decays, indent=12):
        padding = " " * indent
        for branch in decays:
            mode = branch.get("mode", "???")
            if mode.endswith("?"):
                mode = fore(mode, RED)
            chance = f"({branch['chance']}%)" if 'chance' in branch and branch['chance'] != 100 else ""
            if 'chance' not in branch:
                chance = fore("(Not proven)", RED)
            products = branch.get("product", [])
            if not isinstance(products, list): products = [str(products)]
            out = ", ".join(bold(format_isotope(p, fullname)) for p in products)
            animate_print(f"{padding}{bold(display_name)} -> {bold(mode)} -> {out} {chance}")

    if isinstance(info.get("decay"), list):
        animate_print("      ⛓️ - Possible Decays:")
        show_decay(info["decay"])

    if isinstance(info.get("metastable"), dict):
        animate_print("      m - Metastable Isotopes:")
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

def find_isotope(symbol_or_name, mass_number, search_query):
    for val in full_data.values():
        sym = val["general"]["symbol"].lower()
        name = val["general"]["fullname"].lower()
        if symbol_or_name.lower() in (sym, name):
            for isotope, info in val["nuclear"]["isotopes"].items():
                norm_iso_match = re.match(r"^(.*?)(?:\s*-\s*.*)?$", isotope)
                norm_iso = norm_iso_match.group(1) if norm_iso_match else isotope
                if (
                    remove_superscripts(norm_iso).lower() == f"{mass_number}{sym}" or
                    remove_superscripts(norm_iso).lower() == f"{sym}{mass_number}" or
                    norm_iso.lower() == search_query
                ):
                    logging.info(f"Found isotope match: {mass_number}{sym} / {name}")
                    if EXPORT:
                        return {
                            "isotope": isotope,
                            "symbol": sym,
                            "fullname": name,
                            "info": info
                        }
                    print_separator()
                    print_isotope(norm_iso, info, name)
                    print_separator()
                    return True
    return False

def find_element(user_input) -> typing.Tuple[str | None, str | None]:
    user_input = user_input.lower()
    possible_names = []

    for element_candidate in full_data.values():
        name = element_candidate["general"]["fullname"].lower()
        symbol = element_candidate["general"]["symbol"].lower()
        possible_names.extend([name, symbol])

        if user_input == name:
            logging.info(f"Matched element full name: {user_input.capitalize()}")
            return element_candidate, None
        if user_input == symbol:
            logging.info(f"Matched element symbol: {user_input.capitalize()} ({element_candidate['general']['fullname']})")
            return element_candidate, None

    suggestion = difflib.get_close_matches(user_input, possible_names, n=1, cutoff=0.6)
    suggestion = suggestion[0] if suggestion else None

    return None, suggestion

def process_isotope_input(user_input):
    try:
        index = int(user_input) - 1
        search_result = full_data[list(full_data.keys())[index]]
        return search_result, None
    except (ValueError, IndexError):
        symbol_or_name, mass_number = match_isotope_input(user_input)
        if symbol_or_name and mass_number:
            result = find_isotope(symbol_or_name, mass_number, user_input)
            if result:
                return result, None
            return None, None
        return find_element(user_input)

# Other important functions / variables

match random.randint(0, 3):
    case 0:
        tip = "(Tip: You can give this program argv to directly search an element from there. You can even give argv to the ./periodica.sh file too!)"
    case 1:
        tip = "(Tip: Run this script with the --info flag to get information.)"
    case 2:
        tip = "(Tip: Run this script with the --init flag to configure the script.)"
    case 3:
        tip = ""
    case _:
        tip = ""

periodica = bold(gradient("periodica", (156, 140, 255), (140, 255, 245)) if config['truecolor'] else fore("periodica", BLUE))

program_information = f"""
Welcome to {periodica}!
This program provides useful information about the periodic elements, and pretty much everything here was made by the Discord user {bold(fore("Lanzoor", INDIGO))}!
This project started as a fun hobby at around {bold("March 2025")}, but ended up getting taken seriously.
This program was built with {fore("Python", CYAN)}, and uses {fore("JSON", YELLOW)} for configuration files / element database.
The vibrant colors and visuals were done with the help of {italic(bold("ANSI escape codes"))}, although you should note that {bold("some terminals may not have truecolor support.")}
{dim("(You can disable this anytime in the config.json file, or using the --init flag.)")}
There are also other flags you can provide to this program.

- {bold("--info")} - Give this information message
- {bold("--init")} - Edit the settings
- {bold("--update")} - Check for updates
- {bold("--table")} - View the periodic table
- {bold("--export")} \"element\" | \"isotope\" - Export element or isotope to a .json file

{bold("Note: Giving a flag ignores any other arguments, except special ones marked with an asterisk.")}
Anyways, I hope you enjoy this small program. {bold("Please read the README.md file for more information!")}
"""

# Reading json file, and trying to get from GitHub if fails

logging.info("Program initialized.")
try:
    with open(DATA_FILE, 'r', encoding="utf-8") as file:
        full_data = json.load(file)
        logging.info("data.json file was successfully found.")
except json.JSONDecodeError:
    abort_program("data.json file was modified, please do not do so no matter what.")
    animate_print("The data.json file was modified and malformed. Please do not do so, no matter what.\nThis means you need a fresh new data.json file, is it okay for me to get the file for you on GitHub? (y/n)")
    elementdata_malformed = True
except FileNotFoundError:
    logging.warning("data.json file was not found.")
    animate_print("The data.json file was not found. Is it okay for me to get the file for you on GitHub? (y/N)")
    elementdata_malformed = True

if elementdata_malformed:
    confirmation = input("> ").strip().lower()
    if confirmation not in ["y", "yes"]:
        animate_print("Okay, exiting...")
        abort_program("User denied confirmation for fetching the data.json file.")

    url = "https://raw.githubusercontent.com/Lanzoor/periodictable/main/src/data.json"
    animate_print(f"Getting content from {url}, this should not take a while...")

    response = get_response(url)

    animate_print("Successfully got the data.json file! Replacing it...")

    full_data = json.loads(response.text)
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        file.write(response.text)

    logging.info(f"Successfully got the data.json file from {url}.")

# Getting element / isotope

try:
    width = os.get_terminal_size().columns
    height = os.get_terminal_size().lines
except OSError:
    animate_print(bold("What?? So apparently, you aren't running this on a terminal, which is very weird. We will try to ignore this issue, and will determine your terminal width as 80. Please move on and ignore this message."))
    logging.warning("The script ran without a terminal, so failback to reasonable terminal width variable.")
    width = 80
    height = 40

if width <= 80:
    animate_print(fore(f"You are running this program in a terminal that has a width of {bold(width)},\nwhich may be too compact to display and provide the information.\nPlease try resizing your terminal.", RED))
    logging.warning("Not enough width for terminal.")

if len(sys.argv) > 1:
    recognized_flag = (
        create_flag("--info", callable=get_information) or
        create_flag("--init", callable=configurate) or
        create_flag("--update", callable=check_for_update) or
        create_flag("--table", callable=view_table) or
        create_flag("--export", callable=export)
    )

    if not recognized_flag:
        user_input = get_element_argument()

        if not user_input:
            animate_print(fore("No valid element or isotope provided. Falling back to interactive input.", RED))
            logging.warning("Argv missing valid content, fallback to interactive.")
        else:
            logging.info(f"User gave argv: \"{user_input}\"")
            element_data, element_suggestion = process_isotope_input(user_input)

            if element_data is None:
                message = f"Invalid argv.{' Did you mean \"' + bold(element_suggestion) + '\"?' if element_suggestion else ' Falling back to interactive input.'}"
                animate_print(fore(message, YELLOW if element_suggestion else RED))
                logging.warning("Argv invalid, fallback to interactive.")
else:
    logging.warning("Argument not given, falling back to interactive input.")

if element_data is None:
    animate_print(f"Search for an element by name, symbol, or atomic number. {dim(tip)}")
    while True:
        user_input = input("> ").strip().lower()
        logging.info(f"User gave input: \"{user_input}\"")

        element_data, element_suggestion = process_isotope_input(user_input)

        if element_data is not None:
            break

        message = "Not a valid element or isotope."
        if element_suggestion:
            message += f" Did you mean \"{bold(element_suggestion)}\"?"
        animate_print(fore(message, YELLOW if element_suggestion else RED))

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
    lanthanides[atomic_number - LANTHANUM + 3] = fore("▪", GREEN)
elif atomic_number in actinides_range:
    actinides[atomic_number - ACTINIUM + 3] = fore("▪", GREEN)
else:
    periodic_table[period - 1][group - 1] = fore("▪", GREEN)

entries = [
    bold(fore(name, MALE if gender == "male" else FEMALE))
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

subshell_capacities = {'s': 2, 'p': 6, 'd': 10, 'f': 14}
subshell_result = ""
for subshell in subshells:
    if len(subshell) < 3 or not subshell[-1].isdigit():
        logging.warning(f"To the developers, a malformed subshell was detected in {fullname.capitalize()}. Issue: {subshell}")
        continue
    subshell = subshell[:-1] + (convert_superscripts(subshell[-1]) if superscripts else subshell[-1])
    match = re.match(r"(\d)([spdf])(\d+)", subshell)
    if match:
        _, subshell_type, electron_count = match.groups()
        max_capacity = subshell_capacities[subshell_type]
        subshell_result += f"{bold(subshell)} ({electron_count}/{max_capacity}), "
    else:
        subshell_result += f"{bold(subshell)}, "

subshell_result = subshell_result.rstrip(", ")

# Physical properties

melting_point = physical["melt"]
boiling_point = physical["boil"]
atomic_mass = physical["atomic_mass"]
radioactive = general["radioactive"]
half_life = general["half_life"]
density = physical["density"]

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
sound_transmission_speed = measurements["sound_transmission_speed"]

logging.info("Starting output.")

animate_print()
print_header("General")
animate_print()

animate_print(f" 🔡 - Element Name: {bold(fullname)} ({bold(symbol)})")
animate_print(f" Z - Atomic Number: {bold(atomic_number)}")
animate_print(f" 📃 - Description:\n\n    {description}\n")
animate_print(f" 🔍 - Discoverer(s): {discoverers}")
animate_print(f" 🔍 - Discovery Date: {bold(discovery_date)}")
animate_print(f" ↔️ - Period (Row): {bold(period)}")
animate_print(f" ↕️ - Group (Column): {bold(group)}")
animate_print(f" 🎨 - Type: {fore(element_type, types[element_type])}")
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
animate_print(f" ⚛️ - Shells {dim(f"(The electron in {fore("yellow", VALENCE_ELECTRONS_COL)} is the valence electron)")}:\n    {shell_result}")
animate_print(f" 🌀 - Subshells: {subshell_result}")
animate_print(f" 🪞 - Isotopes ({len(isotopes.keys())}): {dim(f"(Decay processes in {fore("red", RED)} need verification. Do not trust them!)")}:")

for isotope, information in isotopes.items():
    print_isotope(isotope, information, fullname)

animate_print()
print_header("Physical Properties")
animate_print()

animate_print(f" 💧 - {fore("Melting Point", MELT_COL)}: {bold(melting_point)}°C = {bold(celcius_to_fahrenheit(melting_point))}°F = {bold(celcius_to_kelvin(melting_point))}K")
animate_print(f" 💨 - {fore("Boiling Point", BOIL_COL)}: {bold(boiling_point)}°C = {bold(celcius_to_fahrenheit(boiling_point))}°F = {bold(celcius_to_kelvin(boiling_point))}K")
animate_print(f" A - Mass Number: {fore(protons, RED)} + {fore(neutrons, BLUE)} = {bold(protons + neutrons)}")
animate_print(f" u - Atomic Mass: {bold(atomic_mass)}g/mol")
animate_print(f" ☢️ - {fore("Radioactive", ORANGE)}: {fore("Yes", GREEN) if radioactive else fore("No", RED)}")
animate_print(f" t1/2 - Half Life: {bold(half_life if not (half_life is None) else fore("Stable", CYAN))}")
animate_print(f" ρ - Density: {bold(density)}g/{cm3}")

animate_print()
print_header("Electronic Properties")
animate_print()

animate_print(f" χ - Electronegativity: {bold(electronegativity)}")
animate_print(f" EA - Electron Affinity: {bold(electron_affinity)}eV = {bold(eV_to_kJpermol(electron_affinity))}kJ/mol")
animate_print(f" IE - {fore("Ionization Energy", MAGENTA)}: {bold(ionization_energy)}eV = {bold(eV_to_kJpermol(ionization_energy))}kJ/mol")
animate_print(f" ⚡️ - {fore("Oxidation States", YELLOW)} {dim(f"(Only the ones that have {fore("color", BLUE)} are activated)")}:\n{"   " + negatives_result}\n{"   " + positives_result}\n")
animate_print(f" ⚡️ - Conductivity Type: {bold(conductivity_type)}")

animate_print()
print_header("Measurements")
animate_print()

animate_print(" r - Radius: ")
animate_print(f"   r_calc - Calculated: {bold(str(radius["calculated"])) + "pm" if not (radius["calculated"] is None) else fore("N/A", CYAN)}")
animate_print(f"   r_emp - Empirical: {bold(str(radius["empirical"])) + "pm" if not (radius["empirical"] is None) else fore("N/A", CYAN)}")
animate_print(f"   r_cov - Covalent: {bold(str(radius["covalent"])) + "pm" if not (radius["covalent"] is None) else fore("N/A", CYAN)}")
animate_print(f"   rvdW - Van der Waals: {bold(str(radius["van_der_waals"])) + "pm" if not (radius["van_der_waals"] is None) else fore("N/A", CYAN)}\n")
animate_print(" 🪨 - Hardness: ")
animate_print(f"   HB - Brinell: {bold(str(hardness["brinell"])) + f"kgf/{mm2}" if not (hardness["brinell"] is None) else fore("None", CYAN)}")
animate_print(f"   H - Mohs: {bold(str(hardness["mohs"]) if not (hardness["mohs"] is None) else fore("None", CYAN))}")
animate_print(f"   HV - Vickers: {bold(str(hardness["vickers"])) + f"kgf/{mm2}" if not (hardness["vickers"] is None) else fore("None", CYAN)}\n")
animate_print(" 🔃 - Moduli: ")
animate_print(f"   K - Bulk Modulus: {bold(str(moduli["bulk"])) + "GPa" if not (moduli["bulk"] is None) else fore("None", CYAN)}")
animate_print(f"   E - Young's Modulus: {bold(str(moduli['young'])) + "GPa" if moduli['young'] is not None else fore('None', CYAN)}")
animate_print(f"   G - Shear Modulus: {bold(str(moduli["shear"])) + "GPa" if not (moduli['shear'] is None) else fore("None", CYAN)}")
animate_print(f"   ν - Poisson's Ratio: {bold(str(moduli["poissons_ratio"])) if not (moduli["poissons_ratio"] is None) else fore("None", CYAN)}\n")
animate_print(f" 📢 - Speed of Sound Transmission: {bold(sound_transmission_speed)}m/s = {bold(sound_transmission_speed / 1000)}km/s")

print_separator()

logging.info("End of program reached. Aborting...")
sys.exit(0)
