import lib.vector as vector

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
  def render(cls, stage, cell, visited_cells=None):
    if stage.get_tile_at(vector.add(cell, (0, -1))) is not Pit:
      return assets.sprites["tomb_pit"]
    else:
      return None

class Escape(DefaultEscape):
  sprite = assets.sprites["stairs_up"]

class TombTileset(Tileset):
    tile_size = TILE_SIZE
    mappings = {
        # ".": Floor,
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
        if not tile in TombTileset.mappings:
            return None

        tile_cls = TombTileset.mappings[tile]
        return tile_cls.render(stage, cell, visited_cells)
