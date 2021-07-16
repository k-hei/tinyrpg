from random import choice
from lib.cell import manhattan, neighborhood
from dungeon.features.room import Room
from dungeon.props.chest import Chest

class ItemRoom(Room):
  def __init__(room, items=[], *args, **kwargs):
    super().__init__(degree=1, *args, **kwargs)
    room.items = items

  def place(room, stage, cell=None, connectors=[]):
    if not super().place(stage, cell, connectors):
      return False
    valid_cells = [c for c in room.get_cells() if not next((d for d in connectors if manhattan(d, c) <= 2), None)]
    items = list(room.items)
    while items and valid_cells:
      cell = choice(valid_cells)
      stage.spawn_elem_at(cell, Chest(items.pop(0)))
      for neighbor in neighborhood(cell, inclusive=True):
        if neighbor in valid_cells:
          valid_cells.remove(neighbor)
    return True
