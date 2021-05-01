from dataclasses import dataclass
from pygame import Surface

@dataclass
class Sprite:
  image: Surface
  pos: tuple[int, int]
  layer: str
  offset: int = 0
