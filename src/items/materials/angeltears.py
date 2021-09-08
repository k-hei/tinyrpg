from dataclasses import dataclass
from items.materials import MaterialItem
from colors.palette import BLUE

@dataclass
class AngelTears(MaterialItem):
  name: str = "AngelTears"
  desc: str = "Said to heal illnesses."
  value: int = 9
  color: int = BLUE
