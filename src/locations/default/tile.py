from pygame import Surface
from dataclasses import dataclass

@dataclass
class Tile:
  solid: bool = False
  opaque: bool = False
  pit: bool = False
  elev: float = 0.0
  direction: tuple = (0, 0)
  sprite: Surface = None

  @staticmethod
  def find_state(stage, cell, visited_cells):
    return cell in visited_cells

  @staticmethod
  def is_of_type(tile, tile_type):
    return tile and issubclass(tile, tile_type)

  @classmethod
  def render(cls, stage, cell, visited_cells):
    return cls.sprite

  def is_solid(tile):
    return not tile or tile.solid

  def is_walkable(tile):
    return tile and not tile.solid and not tile.pit
