from random import choice
from dungeon.features.specialroom import SpecialRoom
from dungeon.props.chest import Chest
from dungeon.actors.eye import Eye as Eyeball
from lib.cell import manhattan

class EnemyRoom(SpecialRoom):
  def __init__(room):
    super().__init__(
      degree=2,
      shape=[("." * 5) for _ in range(4)]
    )

  def get_edges(room):
    room_width, room_height = room.get_size()
    room_x, room_y = room.cell
    return [(x, y) for (x, y) in super().get_edges() if (
      x == room_x + room_width // 2
      or y == room_y + room_height // 2
    )]

  def place(room, stage, connectors, cell=None):
    super().place(stage, connectors, cell)
    room_width, room_height = room.get_size()
    room_x, room_y = room.cell or (0, 0)
    valid_cells = [c for c in room.get_cells() if not next((d for d in connectors if manhattan(d, c) <= 3), None)]
    enemy_count = 2
    while enemy_count and valid_cells:
      cell = choice(valid_cells)
      stage.spawn_elem_at(cell, Eyeball())
      valid_cells.remove(cell)
      enemy_count -= 1
