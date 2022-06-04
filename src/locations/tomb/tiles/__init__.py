import lib.vector as vector
from lib.sprite import Sprite

import assets
from config import TILE_SIZE
from locations.tileset import Tileset
from locations.default.tileset import (
  Floor as DefaultFloor,
  Wall as DefaultWall,
  Pit as DefaultPit,
  Hallway as DefaultHallway,
  Entrance as DefaultEntrance,
  Exit as DefaultExit,
  Escape as DefaultEscape,
  Oasis as DefaultOasis,
  OasisStairs as DefaultOasisStairs,
)

class Floor(DefaultFloor):
  @staticmethod
  def find_state(stage, cell, *_):
    x, y = cell
    return [
      stage.get_tile_at(cell),
      stage.get_tile_at((x, y - 1)),
    ]

  @classmethod
  def render(cls, stage, cell, *_):
    x, y = cell
    if (Pit in stage.get_tile_at((x, y - 1))
    and next((e for e in stage.elems if e.cell[1] < y), None)):
      return Sprite(
        image=assets.sprites["tomb_floor"],
        layer="elems",
        offset=-1,
      )
    else:
      return assets.sprites["tomb_floor"]

class Pit(DefaultPit):
  @staticmethod
  def find_state(stage, cell, visited_cells):
    x, y = cell
    return [
      stage.get_tile_at(cell),
      stage.get_tile_at((x, y - 1)),
      (x, y - 1) in visited_cells,
    ]

  @classmethod
  def render(cls, stage, cell, *_):
    return (assets.sprites["tomb_pit"]
      if Pit not in stage.get_tile_at(vector.add(cell, (0, -1)))
      else None)

class Escape(DefaultEscape):
  sprite = assets.sprites["stairs_up"]

class TombTileset(Tileset):
    tile_size = TILE_SIZE
    mappings = {
        ".": Floor,
        # "#": Wall,
        " ": Pit,
        # ",": Hallway,
        # "<": Entrance,
        # ">": Exit,
        "E": Escape,
        # "O": Oasis,
        # "I": OasisStairs,
    }

    @staticmethod
    def is_tile_solid(tile):
        return False

    @staticmethod
    def render_tile(tile, stage, cell, visited_cells):
        if not tile:
            return None

        return tile.render(stage, cell, visited_cells)
