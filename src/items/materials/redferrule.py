from dataclasses import dataclass
from items.materials import MaterialItem
from colors.palette import RED

@dataclass
class RedFerrule(MaterialItem):
  name: str = "RedFerrule"
  desc: str = "Head of a toxic beast."
  value: int = 26
  color: int = RED
