from dataclasses import dataclass, field
import lib.gamepad as gamepad

@dataclass
class ControlPreset:
  left: str = ""
  right: str = ""
  up: str = ""
  down: str = ""
  confirm: str = ""
  cancel: str = ""
  manage: str = ""
  action: str = ""
  run: str = ""
  turn: str = ""
  item: list[str] = field(default_factory=lambda: [])
  wait: list[str] = field(default_factory=lambda: [])
  ally: str = ""
  skill: str = ""
  inventory: str = ""
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
  item=[gamepad.R, gamepad.TRIANGLE],
  wait=[gamepad.R, gamepad.CIRCLE],
  ally=gamepad.L,
  skill=gamepad.SQUARE,
  inventory=gamepad.TRIANGLE,
  equip=gamepad.START,
  minimap=gamepad.SELECT,
)
