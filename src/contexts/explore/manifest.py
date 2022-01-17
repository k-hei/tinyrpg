from lib.grid import Grid
from lib.bounds import find_bounds
import lib.vector as vector

from contexts.explore.stage import Stage
from contexts.explore.roomdata import RoomData
from dungeon.room import Blob as Room
import tiles.default as tileset
from dungeon.decoder import decode_elem
from helpers.stage import find_tile

def manifest_rooms(rooms, dry=False, seed=None):
  stage_cells = []
  for room in rooms:
    stage_cells += room.cells

  stage_blob = Room(stage_cells, origin=(1, 2))
  stage_offset = vector.subtract(stage_blob.origin, find_bounds(stage_cells).topleft)

  stage_tiles = Grid(size=vector.add(stage_blob.rect.size, (2, 3)))
  stage_tiles.fill(tileset.Wall)

  stage = Stage(
    tiles=stage_tiles,
    rooms=rooms,
    bg="tomb"
  )
  stage.seed = seed

  for room in rooms:
    for cell in room.cells:
      if room.data and room.data.tiles:
        tile = room.get_tile_at(vector.subtract(cell, room.origin))
      else:
        tile = tileset.Floor
      stage_tiles.set(*vector.add(cell, stage_offset), tile)

    if not dry:
      room.origin = vector.add(room.origin, stage_offset)
      room.data and spawn_elems(stage, elem_data=room.data.elems, offset=room.origin)

  return stage, stage_offset

def manifest_room(room):
  room_data = RoomData(**room)

  stage_cells = []
  stage_tiles = Grid(size=vector.add(room_data.size, (2, 3)))
  stage_tiles.fill(tileset.Wall)
  stage_origin = (1, 2)
  for cell, tile in room_data.tiles.enumerate():
    stage_cells.append(cell)
    stage_tiles.set(*vector.add(stage_origin, cell), tile)

  stage_rooms = [Room(cells) for cells in room_data.rooms] or [Room(stage_cells)]
  for room in stage_rooms:
    room.origin = vector.add(room.origin, stage_origin)

  stage = Stage(
    tiles=stage_tiles,
    rooms=stage_rooms,
  )

  if stage.entrance is None:
    stage.entrance = find_tile(stage, tileset.Escape)

  spawn_elems(stage, elem_data=room_data.elems, offset=stage_origin)
  return stage

def spawn_elems(stage, elem_data, offset):
  for elem_cell, elem_name, *elem_props in elem_data:
    elem_props = elem_props[0] if elem_props else {}
    elem = decode_elem(elem_cell, elem_name, elem_props)
    stage.spawn_elem_at(vector.add(offset, elem_cell), elem)
