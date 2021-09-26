from random import shuffle
from lib.cell import manhattan, is_adjacent
from dungeon.actors import DungeonActor
from dungeon.stage import Stage
from dungeon.props.secretdoor import SecretDoor

def gen_elems(stage, room, elems):
  spawn_count = 0
  room_doorways = [c for c in room.get_doorways(stage) if not SecretDoor.exists_at(stage, c)]
  if next((e for e in elems if isinstance(e, DungeonActor)), None):
    valid_cells = [c for c in room.get_cells() if (
      not next((d for d in room_doorways if manhattan(d, c) <= 2), None)
      and stage.is_cell_empty(c)
    )]
  else:
    valid_cells = get_room_bonus_cells(room, stage)
  shuffle(valid_cells)
  while elems and valid_cells:
    cell = valid_cells.pop(0)
    stage.spawn_elem_at(cell, elems.pop(0))
    spawn_count += 1
  return spawn_count

def get_room_bonus_cells(room, stage):
  room_cells = room.get_cells()
  room_doorways = room.get_doorways(stage)
  is_wall = lambda x, y: not stage.is_cell_empty((x, y)) or stage.get_tile_at((x, y)) is Stage.PIT
  is_floor = lambda x, y: stage.get_tile_at((x, y)) is Stage.FLOOR
  bonus_cells = [(x, y) for x, y in room_cells if (
    is_floor(x, y)
    and not next((d for d in room_doorways if is_adjacent(d, (x, y))), None)
    and (
      is_wall(x - 1, y - 1) and is_wall(x - 1, y) and is_wall(x, y - 1) and is_floor(x + 1, y + 1)
      or is_wall(x + 1, y - 1) and is_wall(x + 1, y) and is_wall(x, y - 1) and is_floor(x - 1, y + 1)
      or is_wall(x - 1, y + 1) and is_wall(x - 1, y) and is_wall(x, y + 1) and is_floor(x + 1, y - 1)
      or is_wall(x + 1, y + 1) and is_wall(x + 1, y) and is_wall(x, y + 1) and is_floor(x - 1, y - 1)
    )
  )]
  return bonus_cells
