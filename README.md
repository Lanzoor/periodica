# Installation

Of course, this is a Python script, which means you will need to run it with a Python interpreter.
However, for most cases, I recommend you run the following methods;

## For Linux

**Run these commands, one-by-one.** The method below is heavily recommended, instead of downloading the zipped source code.

```bash
# This gets the GitHub repository, and adds it into the opt folder.
sudo git clone https://github.com/Lanzoor/periodica.git /opt/periodica

# Get inside the folder already!
cd /opt/periodica

# This will create a venv, and install required packages. READ THE SCRIPT FIRST! DO NOT TRUST SOURCES FROM ONLINE. It will create a venv folder. You will need to use sudo here, because /opt is protected by root.
sudo ./build.sh

# Make it executable, so that you don't run into awful problems. This step is required for you to run periodica without using super-user.
sudo chmod +x /opt/periodica/periodica.sh
sudo chown -R $USER:$USER /opt/periodica
chmod -R u+rwX /opt/periodica

# Optional: move it into your /usr/local/bin/ so that you can access it anywhere by running periodica. SUDO IS REQUIRED, /usr/local/bin/ is protected by root.
sudo ln -s /opt/periodica/periodica.sh /usr/local/bin/periodica

# Now let's test it!
periodica
```

## Windows

Unfortunately, at least for now, **this program is not supported by Windows.** So unless you know the manual venv creation, please wait until a Windows version or a workaround is released.

Anyways, that's about it! Have fun messing around, catching bugs, and do note, **you may use the `elementdata.json` file without any credits or permission,** but giving credit will help both clarify stuff and support the creator's hard work!

> *(Unless you try to say that you made the `elementdata.json` file, you will be fine.)*
