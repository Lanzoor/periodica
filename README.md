# Installation

Of course, this is a Python script, which means you will need to run it with a Python interpreter.
However, for most cases, I recommend you run the following methods;

## 🐧 Linux

**Run these commands, one-by-one.** The method below is heavily recommended, instead of downloading the zipped source code.

> Make sure that you have the latest version of Python in your machine! It usually comes with Linux, but just be sure.

```bash
# The following steps require you to run as super-user, since /opt/ and /usr/local/bin/ is protected by root.
# This gets the GitHub repository, and adds it into the opt folder.
sudo git clone https://github.com/Lanzoor/periodica.git /opt/periodica

# Get inside the folder already!
cd /opt/periodica

# This will create a venv, and install required packages. READ THE SCRIPT FIRST! DO NOT TRUST SOURCES FROM ONLINE. It will create a venv folder.
sudo python3 build.py

# Make it executable, so that you don't run into awful problems. This step is required for you to run periodica without using super-user.
sudo chmod +x /opt/periodica/periodica.sh
sudo chown -R $USER:$USER /opt/periodica
sudo chmod -R u+rwX /opt/periodica

# Optional: move it into your /usr/local/bin/ so that you can access it anywhere by typing 'periodica'.
sudo ln -s /opt/periodica/periodica.sh /usr/local/bin/periodica

# Now let's test it!
periodica
```

> ⚠️ Absolutely DO NOT run or use the `periodica.bat` file on Linux! It just won't work, and even if it does, you probably won't be able to access the `main.py` file with `periodica`.

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

### 3. Run the Setup Script

Use this command to set everything up:

```ps1
py build.py
```

This will:

> Create a virtual environment (venv)

> Install all required dependencies inside that venv

### 4. Run the App

Once setup is done, you can run the app in that same terminal:

```ps1
py src/main.py
```

Or open the folder and double-click `main.py` — then select the Python interpreter to open it.

### 5. (Optional) Add the App on your PATH

1. Press the shortcut `Win + R`, and in the input box, type `sysdm.cpl` carefully. Hit `Enter`.
2. You will see a window named `System Properties`. Navigate to the `Advanced` tab. 
3. Click `Environment Variables...` at the bottom.
4. Under `User variables`, select `Path` and click `Edit`. 
5. Click `New`, and paste the full absolute path to the folder containing your `periodica.bat` file.
6. Now make sure to apply and confirm your edits. Exit all tabs.

Now, you can just do this in a fresh terminal;

```ps1
periodica
```

And the project will automatically be runned once you type it.

> ⚠️ **Absolutely DO NOT run the `periodica.sh` or `build.sh` scripts on Windows! They're only made for Linux/macOS and can (and will) cause problems on Windows.**

## 🎉 You're Done!

Go mess around with stuff, find some bugs, contribute improvements, or just enjoy playing with the element database!

> The elementdata.json file is public domain — feel free to use it however you like. **But giving credit helps and shows respect to the effort behind it.** (Just don’t say that you made it, or use it to get profit. That's some real legal trouble right there.)