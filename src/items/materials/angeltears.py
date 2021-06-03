from dataclasses import dataclass
from items.materials import MaterialItem
from palette import BLUE

@dataclass
class AngelTears(MaterialItem):
  name: str = "AngelTears"
  desc: str = "Divine sorrow given form."
  value: int = 9
  color: int = BLUE
