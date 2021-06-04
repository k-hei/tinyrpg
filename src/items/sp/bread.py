from dataclasses import dataclass
from items.sp import SpItem

@dataclass
class Bread(SpItem):
  name: str = "Bread"
  desc: str = "Restores\n10 SP."
  sp: int = 10
  value: int = 7
