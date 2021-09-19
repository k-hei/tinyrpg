from lib.bounds import find_bounds
from lib.cell import add as add_vector, subtract as subtract_vector
from dungeon.stage import Stage
from dungeon.room import Blob
from resolve.elem import resolve_elem

def manifest_stage(rooms, dry=False):
  stage_cells = []
  for room in rooms:
    stage_cells += room.cells
  stage_blob = Blob(stage_cells, origin=(1, 2))
  stage_offset = subtract_vector(stage_blob.origin, find_bounds(stage_cells).topleft)
  stage = Stage(add_vector(stage_blob.rect.size, (2, 2)))
  stage.fill(Stage.WALL)
  for room in rooms:
    for cell in room.cells:
      if room.data:
        tile_id = room.get_tile_at(subtract_vector(cell, room.origin))
        tile = Stage.TILE_ORDER[tile_id]
        stage.set_tile_at(add_vector(cell, stage_offset), tile)
      else:
        stage.set_tile_at(add_vector(cell, stage_offset), Stage.FLOOR)
    if not dry:
      room.origin = add_vector(room.origin, stage_offset)
      if room.data:
        for cell, elem_id, *props in room.data.elems:
          props = props[0] if props else {}
          stage.spawn_elem_at(add_vector(room.origin, cell), resolve_elem(elem_id)(**props))
  return stage, stage_offset
