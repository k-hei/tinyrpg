from dungeon.features import Feature
from lib.cell import add

class Room(Feature):
  def __init__(room):
    super().__init__()
    room.cell = None

  def validate(room, cell, slots):
    cells = [add(c, cell) for c in room.get_cells()]
    cells = [(x, y) for x, y in cells if x % 2 == 1 and y % 3 == 1]
    for cell in cells:
      if cell not in slots:
        return False
    return True

  def filter_slots(room, slots):
    return [s for s in slots if room.validate(s, slots)]
