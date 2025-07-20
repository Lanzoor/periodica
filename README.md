# Installation

Of course, this is a Python script, which means you will need to run it with a Python interpreter.
However, for most cases, I recommend you run the following methods;

## 🐧 Linux

**Run these commands, one-by-one.** The method below is heavily recommended, instead of downloading the zipped source code.

> Make sure that you have the latest version of Python in your machine! It usually comes with Linux, but just be sure.

```bash
# Clone the GitHub repository into a proper workspace directory.
git clone https://github.com/Lanzoor/periodica.git ~/dev/periodica

# This will create a virtual environment and install required packages. Also, it will create a symlink to ~/.local/bin/periodica, where you can run the program without having to worry.
# READ THE SCRIPT BEFORE RUNNING IT. DO NOT TRUST FILES FROM ONLINE BY DEFAULT.
python3 ~/dev/periodica/build.py

# Now test it:
periodica
```

## 🪟 Windows

### 1. Install Python

Windows doesn’t come with Python by default — and even if it does, it’s probably outdated.
Go to the official Python download page:

👉 https://www.python.org/downloads/

Click the **"Download Python"** button and install it.

After installing, open a terminal (Command Prompt or PowerShell) and verify it works:

```ps1
py --version
py -m pip --version
```

> If py doesn’t work, try using python or python3.

### 2. Get the Source Code

Click the **"<> Code ▼"** button on the GitHub repo, then choose **"🗂️ Download ZIP"**.
Extract the contents somewhere convenient, then open a terminal in that folder.

### 3. Install the required dependencies

In that same terminal, run;

```ps1
py -m pip install -r requirements.txt
```

### 4. Run the App

Once setup is done, you can run the app in that same terminal:

```ps1
py src/main.py
```

Or open the folder and double-click `main.py` — then select the Python interpreter to open it.

> ⚠️ **Absolutely DO NOT run the `periodica.sh` or `build.py` scripts on Windows! They're only made for Linux/macOS and can (and will) cause problems on Windows.**

> **Please do not complain about the Windows installation process.** This program was built with Linux in mind.

## 🎉 You're Done!

Go mess around with stuff, find some bugs, contribute improvements, or just enjoy playing with the element database!

> The data.json file is public domain — feel free to use it however you like. **But giving credit helps and shows respect to the effort behind it.** (Just don’t say that you made it, or use it to get profit. That's some real legal trouble right there.)

# IMPORTANT NOTE: Since how the program validates isotope names, any unadded isotope names will result in weird behaviours. Please, DO NOT TRUST THE DAUGHTER ISOTOPES OF RECENTLY ADDED ELEMENTS.
