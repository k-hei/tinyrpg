from dataclasses import dataclass
from items.hp import HpItem

@dataclass
class Potion(HpItem):
  name: str = "Potion"
  desc: str = "Restores\n20 HP."
  hp: int = 20
  value: int = 25
