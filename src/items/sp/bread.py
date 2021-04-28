from dataclasses import dataclass
from items.sp import SpItem

@dataclass(frozen=True)
class Bread(SpItem):
  name: str = "Bread"
  desc: str = "Restores 10 SP."
  sp: int = 10
