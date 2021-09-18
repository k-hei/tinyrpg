from lib.bounds import find_bounds
from lib.cell import add as add_vector, subtract as subtract_vector
from dungeon.stage import Stage
from dungeon.room import Blob
from resolve.elem import resolve_elem

def manifest_stage(rooms):
  stage_cells = []
  for room in rooms:
    stage_cells += room.cells
  stage_offset = subtract_vector((1, 1), find_bounds(stage_cells).topleft)
  stage_blob = Blob(stage_cells, origin=(1, 1))
  stage = Stage(add_vector(stage_blob.rect.size, (2, 2)))
  stage.fill(Stage.WALL)
  for room in rooms:
    for cell in room.cells:
      x, y = subtract_vector(cell, room.origin)
      cell = add_vector(cell, stage_offset)
      if room.data:
        tile_id = room.data.tiles[y * room.width + x]
        tile = Stage.TILE_ORDER[tile_id]
        stage.set_tile_at(cell, tile)
      else:
        stage.set_tile_at(cell, Stage.FLOOR)
  return stage, stage_offset
