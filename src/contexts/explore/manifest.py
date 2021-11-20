from contexts.explore.stage import Stage
from contexts.explore.roomdata import RoomData
from lib.grid import Grid
import lib.vector as vector
import tiles.default as tileset

def manifest_stage(room):
  room_data = RoomData(**room)
  stage_tiles = Grid(
    size=vector.add(room_data.size, (2, 2))
  )
  stage_tiles.fill(tileset.Wall)
  for cell, tile in room_data.tiles.enumerate():
    stage_tiles.set(*vector.add(cell, (1, 1)), tile)
  return Stage(
    tiles=stage_tiles,
  )
