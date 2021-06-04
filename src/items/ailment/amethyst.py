from dataclasses import dataclass
from items.ailment import AilmentItem

@dataclass
class Amethyst(AilmentItem):
  name: str = "Amethyst"
  desc: str = "Dispels all ailments."
  sprite: str = "gem"
  ailment: str = "any"
  value: int = 80
