# Installation

Of course, this is a Python script, which means you will need to run it with a Python interpreter.
However, for most cases, I recommend you run the following command;

## For Linux

**First, go inside the periodictable directory.** This step is important. And then, **run the following command:**

```bash
./build.sh
```

This will install all required packages. No bloat, only the needed ones.
This is the same as doing `pip install -r ./requirements.txt`, but the shell script in the directory will make it way cleaner.

> If you are unsure about the `./build.sh` and the `./periodictable.sh` files in the directory, just read them yourself!

This also means that you can **run** the file too with the following;

```bash
./periodictable.sh
```

And if you need to give argv;

```bash
./periodictable.sh YOUR_ARGUMENTS_GO_HERE
```

Instead of having to step into the src directory, running python, stuff like that.

## Windows

Just like the Linux build method, first, **go inside the periodictable directory,** and run this script for building;

```ps1
.\build.ps1
```

> Again, **read the file first if you do not trust it.**

And, run this script for running the program itself;

```ps1
.\periodictable.ps1
```

You can also give argv.

```ps1
.\periodictable.ps1 YOUR_ARGUMENTS_GO_HERE
```

Anyways, that's about it! Have fun messing around, and do note, **you may use the `elementdata.json` file without any credits or permission,** but giving credit will help clarify stuff!

> *(Unless you try to say that you made the `elementdata.json` file, you will be fine.)*
