from dataclasses import dataclass
from items.sp import SpItem

@dataclass
class Cheese(SpItem):
  name: str = "Cheese"
  desc: str = "Restores\n5 SP."
  sp: int = 5
  value: int = 5
