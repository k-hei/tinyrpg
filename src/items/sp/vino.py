from dataclasses import dataclass
from items.sp import SpItem

@dataclass
class Vino(SpItem):
  name: str = "Vino"
  desc: str = "Restores\n50 SP."
  sp: int = 50
  value: int = 40
  rarity: int = 3
