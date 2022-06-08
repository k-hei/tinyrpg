from random import shuffle
from lib.cell import manhattan, is_adjacent
from dungeon.actors import DungeonActor
from dungeon.props.secretdoor import SecretDoor
import locations.default.tileset as tileset
from config import TILE_SIZE


def gen_elems(stage, room, elems):
  spawn_count = 0
  room_doorways = [c for c in room.get_doorways(stage)]

  if next((e for e in elems if isinstance(e, DungeonActor)), None):
    valid_cells = [c for c in room.get_cells() if (
      not next((d for d in room_doorways if manhattan(d, c) <= 2), None)
    )]
  else:
    valid_cells = get_room_bonus_cells(room, stage)

  valid_cells = [c for c in valid_cells
    if stage.is_cell_empty(c)
    and not stage.is_tile_at_pit(c)]

  shuffle(valid_cells)
  while elems and valid_cells:
    cell = valid_cells.pop(0)
    stage.spawn_elem_at(cell, elems.pop(0))
    spawn_count += 1

  return spawn_count

def get_room_bonus_cells(room, stage):
  room_cells = room.cells
  room_doorways = room.get_doorways(stage)
  is_wall = lambda x, y: (
    not stage.is_cell_empty((x, y))
    or stage.is_tile_at_pit((x, y))
  )
  is_floor = lambda x, y: (
    stage.is_tile_at_of_type((x, y), tileset.Floor)
    and not stage.is_cell_occupied((x, y), TILE_SIZE)
  )
  bonus_cells = [(x, y) for x, y in room_cells if (
    is_floor(x, y)
    and not next((d for d in room_doorways if is_adjacent(d, (x, y))), None)
    and (
      is_wall(x - 1, y - 1) and is_wall(x - 1, y) and is_wall(x, y - 1) and not is_wall(x + 1, y + 1) and is_floor(x + 1, y + 1)
      or is_wall(x + 1, y - 1) and is_wall(x + 1, y) and is_wall(x, y - 1) and not is_wall(x - 1, y + 1) and is_floor(x - 1, y + 1)
      or is_wall(x - 1, y + 1) and is_wall(x - 1, y) and is_wall(x, y + 1) and not is_wall(x + 1, y - 1) and is_floor(x + 1, y - 1)
      or is_wall(x + 1, y + 1) and is_wall(x + 1, y) and is_wall(x, y + 1) and not is_wall(x - 1, y - 1) and is_floor(x - 1, y - 1)
    )
  )]
  return bonus_cells
