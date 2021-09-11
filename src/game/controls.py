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
  ally: str
  skill: list[str]
  item: list[str]
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
  ally=gamepad.L,
  skill=[gamepad.SQUARE],
  item=[gamepad.TRIANGLE],
  equip=gamepad.START,
  minimap=gamepad.SELECT,
)
