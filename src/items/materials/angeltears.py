from dataclasses import dataclass
from items import Item
from palette import GRAY

@dataclass
class AngelTears(Item):
  name: str = "AngelTears"
  desc: str = "The tears of a divine entity."
  color: int = GRAY
  value: int = 5
