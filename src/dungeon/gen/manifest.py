from lib.bounds import find_bounds
from lib.cell import add as add_vector, subtract as subtract_vector
from dungeon.stage import Stage
from dungeon.room import Blob as Room
from dungeon.roomdata import RoomData
from dungeon.decoder import decode_elem
from resolve.elem import resolve_elem

def manifest_stage(rooms, dry=False, seed=None):
  stage_cells = []
  for room in rooms:
    stage_cells += room.cells
  stage_blob = Room(stage_cells, origin=(1, 2))
  stage_offset = subtract_vector(stage_blob.origin, find_bounds(stage_cells).topleft)
  stage = Stage(add_vector(stage_blob.rect.size, (2, 3)))
  stage.rooms = rooms
  stage.seed = seed
  stage.fill(Stage.WALL)
  for room in rooms:
    for cell in room.cells:
      if room.data and room.data.tiles:
        tile_id = room.get_tile_at(subtract_vector(cell, room.origin))
        tile = Stage.TILE_ORDER[tile_id]
        stage.set_tile_at(add_vector(cell, stage_offset), tile)
      else:
        stage.set_tile_at(add_vector(cell, stage_offset), Stage.FLOOR)
    if not dry:
      room.origin = add_vector(room.origin, stage_offset)
      for elem_cell, elem_name, *elem_props in (room.data.elems if room.data else []):
        elem_props = elem_props[0] if elem_props else {}
        elem = decode_elem(elem_cell, elem_name, elem_props)
        stage.spawn_elem_at(add_vector(room.origin, elem_cell), elem)
  return stage, stage_offset

def manifest_stage_from_room(room):
  if type(room) is RoomData:
    room = Room(data=room)

  room.origin = (1, 2)
  stage = Stage((room.width + 2, room.height + 3))
  stage.fill(Stage.WALL)
  stage.rooms = [room]

  for y in range(room.height):
    for x in range(room.width):
      tile_id = room.data.tiles[y * room.width + x]
      tile = Stage.TILE_ORDER[tile_id]
      stage.set_tile_at(add_vector(room.origin, (x, y)), tile)

  for elem_cell, elem_name, *elem_props in room.data.elems:
    elem_props = elem_props[0] if elem_props else {}
    elem = decode_elem(elem_cell, elem_name, elem_props)
    stage.spawn_elem_at(add_vector(room.origin, elem_cell), elem)

  door_cell = None
  if room.data.edges:
    room.data.edges.sort(key=lambda c: c[1])
    print(room.data.edges)
    for i in range(max(1, room.data.degree)):
      door_cell = add_vector(room.origin, room.data.edges[i])
      door = resolve_elem(room.data.doors)()
      stage.set_tile_at(door_cell, Stage.HALLWAY)
      stage.spawn_elem_at(door_cell, door)

  if door_cell:
    stage.entrance = door_cell
    door.open()
  else:
    stage.entrance = stage.find_tile(stage.STAIRS_EXIT)

  room.on_place(stage)
  return stage
