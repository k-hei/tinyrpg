from dataclasses import dataclass
from items.ailment import AilmentItem

@dataclass(frozen=True)
class Antidote(AilmentItem):
  name: str = "Antidote"
  desc: str = "Cures poison."
  ailment: str = "poison"
