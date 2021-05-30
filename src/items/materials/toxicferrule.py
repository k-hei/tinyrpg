from dataclasses import dataclass
from items.materials import MaterialItem

@dataclass
class ToxicFerrule(MaterialItem):
  name: str = "ToxicFerrule"
  desc: str = "Head of a toxic beast."
  value: int = 13
