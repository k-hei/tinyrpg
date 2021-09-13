from dataclasses import dataclass
import lib.gamepad as gamepad

@dataclass
class ControlPreset:
  confirm: str
  cancel: str
  manage: str
  action: str
  run: str
  turn: str
  throw: list[str]
  wait: list[str]
  use: list[str]
  ally: str
  skill: str
  item: str
  equip: str
  minimap: str

TYPE_A = ControlPreset(
  confirm=gamepad.CIRCLE,
  cancel=gamepad.CROSS,
  manage=gamepad.SQUARE,
  action=gamepad.CIRCLE,
  run=gamepad.CROSS,
  turn=gamepad.R,
  throw=[gamepad.R, gamepad.CIRCLE],
  wait=[gamepad.R, gamepad.CROSS],
  use=[gamepad.R, gamepad.TRIANGLE],
  ally=gamepad.L,
  skill=gamepad.SQUARE,
  item=gamepad.TRIANGLE,
  equip=gamepad.START,
  minimap=gamepad.SELECT,
)
