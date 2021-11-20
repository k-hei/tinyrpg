from pygame import Surface
from dataclasses import dataclass
from types import FunctionType as func

@dataclass
class Tile:
  solid: bool = False
  opaque: bool = False
  pit: bool = False
  elev: float = 0.0
  direction: tuple = (0, 0)
  sprite: Surface = None
  render: func = None
