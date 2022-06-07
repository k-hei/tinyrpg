from pygame import Surface
from dataclasses import dataclass
import assets


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
  def is_tile(tile):
    return tile and isinstance(tile, type) and issubclass(tile, Tile)

  @staticmethod
  def is_of_type(tile, tile_type):
    return (tile
      and isinstance(tile, type)
      and (tile is tile_type or issubclass(tile, tile_type)))

  @classmethod
  def render(cls, stage, cell, visited_cells):
    return (cls.sprite
      if isinstance(cls.sprite, Surface)
      else assets.sprites[cls.sprite])

  def is_solid(tile):
    return not tile or tile.solid

  def is_walkable(tile):
    return tile and not tile.solid and not tile.pit
