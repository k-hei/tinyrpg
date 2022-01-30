from locations.default.tile import Tile

class Floor(Tile):
  pass

class Wall(Tile):
  solid = True
  opaque = True

class Pit(Tile):
  pit = True

class Hallway(Tile):
  pass

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
