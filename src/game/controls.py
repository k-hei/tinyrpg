from dataclasses import dataclass, field
import lib.gamepad as gamepad

@dataclass
class ControlPreset:
  LEFT: str = ""
  RIGHT: str = ""
  UP: str = ""
  DOWN: str = ""
  A: str = ""
  B: str = ""
  X: str = ""
  Y: str = ""
  L: str = ""
  R: str = ""
  SELECT: str = ""
  START: str = ""
  confirm: str = ""
  cancel: str = ""
  manage: str = ""
  run: str = ""
  turn: str = ""
  item: list[str] = field(default_factory=lambda: [])
  wait: list[str] = field(default_factory=lambda: [])
  ally: str = ""
  shortcut: str = ""
  skill: str = ""
  inventory: str = ""
  equip: str = ""
  minimap: str = ""

TYPE_NULL = ControlPreset()
TYPE_A = ControlPreset(
  LEFT=gamepad.LEFT,
  RIGHT=gamepad.RIGHT,
  UP=gamepad.UP,
  DOWN=gamepad.DOWN,
  A=gamepad.A,
  B=gamepad.B,
  X=gamepad.X,
  Y=gamepad.Y,
  L=gamepad.L,
  R=gamepad.R,
  SELECT=gamepad.SELECT,
  START=gamepad.START,
  confirm=gamepad.CIRCLE,
  cancel=gamepad.CROSS,
  manage=gamepad.SQUARE,
  run=gamepad.CROSS,
  turn=gamepad.R,
  item=[gamepad.R, gamepad.TRIANGLE],
  wait=[gamepad.R, gamepad.CIRCLE],
  shortcut=[gamepad.R, gamepad.SQUARE],
  ally=gamepad.L,
  skill=gamepad.SQUARE,
  inventory=gamepad.TRIANGLE,
  equip=gamepad.START,
  minimap=gamepad.SELECT,
)
