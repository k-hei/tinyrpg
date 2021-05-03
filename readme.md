# tinyrpg
> tiny dungeon crawler project

View the latest builds for this project on the [releases page](https://github.com/semibran/tinyrpg/releases).

## development
Requires Python 3 and GNU Make 3.8.2+.

```sh
# Run from source
> make

# Create Unix executable (for use on Mac)
> make build
```

To create an .exe on Windows, use [pyinstaller](https://pypi.org/project/pyinstaller/).
```sh
> py -m PyInstaller --onefile -w src/main.py
```

Note that for all builds, the `assets/` folder must be stored in the same folder as the executable in order for the game to run. (This behavior will be amended towards the end of the project lifecycle.)
