from dataclasses import dataclass
from items.materials import MaterialItem
from colors.palette import GREEN

@dataclass
class CrownJewel(MaterialItem):
  name: str = "CrownJewel"
  desc: str = "A national treasure."
  value: int = 42
  color: int = GREEN
