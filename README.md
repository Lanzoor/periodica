# Installation

Of course, this is a Python script, which means you will need to run it with a Python interpreter.
However, for most cases, I recommend you run the following methods;

## For Linux

**Run these commands, one-by-one.** The method below is heavily recommended, instead of downloading the zipped source code.
Make sure that you have the latest version of Python in your machine! It usually comes with Linux, but just be sure.

```bash
# The following steps require you to run as super-user, since /opt/ and /usr/local/bin/ is protected by root.
# This gets the GitHub repository, and adds it into the opt folder.
sudo git clone https://github.com/Lanzoor/periodica.git /opt/periodica

# Get inside the folder already!
cd /opt/periodica

# This will create a venv, and install required packages. READ THE SCRIPT FIRST! DO NOT TRUST SOURCES FROM ONLINE. It will create a venv folder.
sudo ./build.sh

# Make it executable, so that you don't run into awful problems. This step is required for you to run periodica without using super-user.
sudo chmod +x /opt/periodica/periodica.sh
sudo chown -R $USER:$USER /opt/periodica
sudo chmod -R u+rwX /opt/periodica

# Optional: move it into your /usr/local/bin/ so that you can access it anywhere by typing 'periodica'.
sudo ln -s /opt/periodica/periodica.sh /usr/local/bin/periodica

# Now let's test it!
periodica
```

## Windows

### Download the Python Interpreter

Unfortunately, **the Python interpreter does not come with your machine by default.** And even if it does, it is most likely very outdated.
So, go to the official Python interpreter download page: <https://www.python.org/downloads/>
And click **"Download Python"**.

After you download the Python interpreter, run the following commands in your terminal to make sure it's installed properly:

```ps1
py --version
py -m pip --version
```

(Make sure to replace the "py" keyword to something else if it does not work.)

### Download the Source Code

Now, download the zipped source code by clicking the **"<> Code ▼"** button in the GitHub repository, and clicking **"🗂️ Download ZIP"** button.
The next thing you probably should do is install the required packages. Head into the directory of whatever place you downloaded the ZIP file, and run;

```ps1
py -m pip install -r requirements.txt
```

This is the recommended way to install packages, a global install.
Now, just head inside the src folder, and **double-click the main.py file.** It will show you what program should it open the program for you, **select the Python interpreter.**

Anyways, that's about it! Have fun messing around, catching bugs, and do note, **you may use the `elementdata.json` file without any credits or permission,** but giving credit will help both clarify stuff and support the creator's hard work!

> *(Unless you try to say that you made the `elementdata.json` file, you will be fine.)*
