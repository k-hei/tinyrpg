from pygame import Surface
from locations.default.tile import Tile
from colors.palette import BLACK
from config import TILE_SIZE


black_square = Surface((TILE_SIZE, TILE_SIZE))
black_square.fill(BLACK)


class Floor(Tile):
  pass

class Wall(Tile):
  solid = True
  opaque = True

class Pit(Tile):
  pit = True

class Hallway(Tile):
  sprite = black_square

class Entrance(Tile):
  pass

class Escape(Entrance):
  pass

class Exit(Tile):
  pass

class Oasis(Tile):
  elev = -1.0

class OasisStairs(Tile):
  elev = -0.5

mappings = {}
