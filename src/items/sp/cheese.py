from dataclasses import dataclass
from items.sp import SpItem

@dataclass(frozen=True)
class Cheese(SpItem):
  name: str = "Cheese"
  desc: str = "Restores 5 SP."
  sp: int = 5
