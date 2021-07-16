from random import choice
from lib.cell import manhattan
from dungeon.features.room import Room
from dungeon.props.chest import Chest
from dungeon.actors.eye import Eye as Eyeball

class EnemyRoom(Room):
  def __init__(room, enemies=[], degree=2, *args, **kwargs):
    super().__init__(
      degree=degree,
      *args,
      **kwargs
    )
    room.enemies = enemies

  def place(room, stage, cell=None, connectors=[]):
    if not super().place(stage, cell, connectors):
      return False
    valid_cells = [c for c in room.get_cells() if not next((d for d in connectors if manhattan(d, c) <= 2), None)]
    enemies = list(room.enemies)
    while enemies and valid_cells:
      cell = choice(valid_cells)
      stage.spawn_elem_at(cell, enemies.pop(0))
      valid_cells.remove(cell)
    return True
