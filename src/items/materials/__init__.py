from dataclasses import dataclass
from items import Item
from palette import GRAY

@dataclass
class MaterialItem(Item):
  color: int = GRAY
