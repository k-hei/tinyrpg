from dataclasses import dataclass
from items.materials import MaterialItem
from palette import PURPLE

@dataclass
class ToxicFerrule(MaterialItem):
  name: str = "ToxicFerrule"
  desc: str = "Head of a toxic beast."
  value: int = 13
  color: int = PURPLE
