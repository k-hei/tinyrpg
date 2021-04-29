from dataclasses import dataclass
from items.sp import SpItem

@dataclass
class Fish(SpItem):
  name: str = "Fish"
  desc: str = "Restores 20 SP."
  sp: int = 20
