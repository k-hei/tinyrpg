from dataclasses import dataclass
from sprite import Sprite

@dataclass
class Decor:
  cell: tuple[int, int]
  sprite: Sprite
