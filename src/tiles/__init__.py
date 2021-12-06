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

  def is_solid(tile):
    return not tile or tile.solid

  def is_walkable(tile):
    return tile and not tile.solid and not tile.pit
