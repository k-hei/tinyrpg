from dataclasses import dataclass
from items.sp import SpItem

@dataclass
class Fish(SpItem):
  name: str = "Fish"
  desc: str = "Restores\n20 SP."
  sp: int = 20
  value: int = 15
  rarity: int = 2
