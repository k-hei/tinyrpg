from dataclasses import dataclass
from items.materials import MaterialItem
from colors.palette import VIOLET

@dataclass
class LuckyChoker(MaterialItem):
  name: str = "LuckyChoker"
  desc: str = "Worn by those in the afterlife."
  value: int = 34
  color: int = VIOLET
