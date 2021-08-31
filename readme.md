# tinyrpg
> tiny dungeon crawler project

View the latest builds for this project on the [releases page](https://github.com/semibran/tinyrpg/releases).

## controls
### dungeon
- Enter: Interact/Use skill
- Backtick/Backslash: Skip turn (Hold to recover)
- Backspace: Inventory menu
- B: Custom menu
- M: Open minimap
- Tab: Swap characters (if applicable)
- Ctrl+D: Debug menu

### system
- Ctrl+=: Scale up window
- Ctrl+-: Scale down window
- Ctrl+F: Toggle fullscreen
- Ctrl+R: Reset to initial game state

## development
Requires Python 3 and GNU Make 3.8.2+.

```sh
> pip install pygame pyinstaller

# Run from source
> make

# Resolve static imports
> make imports

# Create Unix executable
> make build
```

To create an .exe on Windows, use [pyinstaller](https://pypi.org/project/pyinstaller/).
```sh
> py -m pip install pygame pyinstaller
> py -m PyInstaller -Fwn tinyrpg src/demo.py
```

`pytest` is an optional dependency. Use for running unit tests:
```sh
> pip install pytest
> make test
```
