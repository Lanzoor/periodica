# Installation

Of course, this is a Python script, which means you will need to run it with a Python interpreter.
However, for most cases, I recommend you run the following methods;

## For Linux

**Run these commands, one-by-one.** The method below is heavily recommended, instead of downloading the zipped source code.

```bash
# This gets the GitHub repository
git clone https://github.com/Lanzoor/periodica.git

# Get inside the folder already!
cd periodica

# Create a venv, and install required packages. READ THE SCRIPT FIRST! DO NOT TRUST SOURCES FROM ONLINE. It will create a venv folder.
./build.sh

# Make it executable.
chmod +x periodica.sh

# Optional: move it into your /usr/local/bin/ so that you can access it anywhere by running periodica
sudo mv periodica.sh /usr/local/bin/periodica

# Now let's test it!
periodica
```

## Windows

Unfortunately, at least for now, **this program is not supported by Windows.** So unless you know the manual venv creation, please wait until a Windows version or a workaround is released.

Anyways, that's about it! Have fun messing around, catching bugs, and do note, **you may use the `elementdata.json` file without any credits or permission,** but giving credit will help both clarify stuff and support the creator's hard work!

> *(Unless you try to say that you made the `elementdata.json` file, you will be fine.)*
