from dataclasses import dataclass
from items.materials import MaterialItem

@dataclass
class AngelTears(MaterialItem):
  name: str = "AngelTears"
  desc: str = "Divine sorrow given form."
  value: int = 5
