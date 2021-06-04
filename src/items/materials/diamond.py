from dataclasses import dataclass
from items.materials import MaterialItem
from palette import GRAY

@dataclass
class Diamond(MaterialItem):
  name: str = "Diamond"
  desc: str = "A precious stone."
  sprite: str = "gem"
  color: tuple[int, int, int] = GRAY
  value: int = 1000
