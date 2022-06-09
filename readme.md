# tinyrpg
> tiny dungeon crawler project

View the latest builds for this project on the [releases page](https://github.com/semibran/tinyrpg/releases).

## gamepad controls
NOTE: Gamepad must be connected before opening the game (for now). Alternatively, connect and then perform a hard reset (Ctrl+Shift+R).
- **A/Circle**: Confirm, Interact, Attack
- **B/Cross**: Run, Cancel
- **X/Square**: Use skill
- **Y/Triangle**: Use item
- **L/L1**: Switch characters
- **R/R1**:
  - **+D-pad**: Change facing direction
  - **+A/Circle**: Skip your turn
  - **+B/Cross**: Unused (dodge roll)
  - **+X/Square**: Unused (skill shortcut)
  - **+Y/Triangle**: Pick up/throw item
- **SELECT**: View minimap
- **START**: Open equip menu

## keyboard controls
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
> py -m pip install pygame pyinstaller pillow zstd
> py -m PyInstaller -Fwn tinyrpg src/demo.py
```

`pytest` is an optional dependency. Use for running unit tests:
```sh
> pip install pytest
> make test
```
