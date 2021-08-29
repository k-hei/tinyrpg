from dataclasses import dataclass
from items.materials import MaterialItem
from colors.palette import GREEN

@dataclass
class Beetle(MaterialItem):
  name: str = "Buge"
  desc: str = "A bug found in the tombs."
  sprite: str = "beetle"
  color: tuple[int, int, int] = GREEN
  value: int = 5
