from random import choice
from lib.cell import subtract as subtract_vector, neighborhood
from dungeon.props.palm import Palm
from dungeon.props.door import Door

def on_place(room, stage):
  palms_left = 3
  valid_cells = [c for c in room.cells if (
    stage.get_tile_at(c) == stage.FLOOR
    and not next((n for n in neighborhood(c, radius=2) if (
      next((e for e in stage.get_elems_at(n) if isinstance(e, Door)), None)
    )), None)
  )]
  while palms_left and valid_cells:
    cell = choice(valid_cells)
    valid_cells.remove(cell)
    stage.spawn_elem_at(cell, Palm())
    palms_left -= 1
