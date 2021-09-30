from dataclasses import dataclass, field
import lib.gamepad as gamepad

@dataclass
class ControlPreset:
  confirm: str = ""
  cancel: str = ""
  manage: str = ""
  action: str = ""
  run: str = ""
  turn: str = ""
  throw: list[str] = field(default_factory=lambda: [])
  wait: list[str] = field(default_factory=lambda: [])
  ally: str = ""
  skill: str = ""
  item: str = ""
  equip: str = ""
  minimap: str = ""

TYPE_NULL = ControlPreset()
TYPE_A = ControlPreset(
  confirm=gamepad.CIRCLE,
  cancel=gamepad.CROSS,
  manage=gamepad.SQUARE,
  action=gamepad.CIRCLE,
  run=gamepad.CROSS,
  turn=gamepad.R,
  throw=[gamepad.R, gamepad.TRIANGLE],
  wait=[gamepad.R, gamepad.CIRCLE],
  ally=gamepad.L,
  skill=gamepad.SQUARE,
  item=gamepad.TRIANGLE,
  equip=gamepad.START,
  minimap=gamepad.SELECT,
)
