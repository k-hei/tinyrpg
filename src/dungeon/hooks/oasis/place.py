from random import choice, shuffle
from lib.cell import subtract as subtract_vector, neighborhood, manhattan
from dungeon.props.palm import Palm
from dungeon.props.door import Door

def on_place(room, stage):
  palms_left = 3
  door_cells = [c for c in room.edges if next((e for e in stage.get_elems_at(c) if isinstance(e, Door)), None)]
  start = door_cells[0]
  valid_cells = [start]
  stack = [start]
  while stack:
    cell = stack.pop()
    for neighbor in neighborhood(cell):
      if (neighbor in valid_cells
      or stage.get_tile_at(neighbor) is not stage.FLOOR
      or next((e for e in stage.get_elems_at(neighbor) if e.solid), None)
      ):
        continue
      stack.append(neighbor)
      valid_cells.append(neighbor)
  valid_cells = [c for c in valid_cells if manhattan(c, start) > 2]
  shuffle(valid_cells)
  while palms_left and valid_cells:
    cell = valid_cells.pop()
    stage.spawn_elem_at(cell, Palm())
    palms_left -= 1
