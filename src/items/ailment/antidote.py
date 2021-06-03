from dataclasses import dataclass
from items.ailment import AilmentItem

@dataclass
class Antidote(AilmentItem):
  name: str = "Antidote"
  desc: str = "Cures poison."
  ailment: str = "poison"
  value: int = 20
