from contexts.explore.stage import Stage
from contexts.explore.roomdata import RoomData
from lib.grid import Grid
import lib.vector as vector
import tiles.default as tileset
from dungeon.decoder import decode_elem

def manifest_stage(room):
  room_data = RoomData(**room)

  stage_tiles = Grid(size=vector.add(room_data.size, (2, 3)))
  stage_tiles.fill(tileset.Wall)
  for cell, tile in room_data.tiles.enumerate():
    stage_tiles.set(*vector.add((1, 2), cell), tile)
  stage = Stage(tiles=stage_tiles)

  for elem_cell, elem_name, *elem_props in room_data.elems:
    elem_props = elem_props[0] if elem_props else {}
    elem = decode_elem(elem_cell, elem_name, elem_props)
    stage.spawn_elem_at(vector.add((1, 2), elem_cell), elem)

  return stage
