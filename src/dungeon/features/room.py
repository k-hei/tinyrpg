from dungeon.features import Feature
from lib.cell import add

class Room(Feature):
  def __init__(room, size):
    super().__init__()
    room.size = size
    room.cell = None

  def get_width(room):
    width, _ = room.get_size()
    return width

  def get_height(room):
    _, height = room.get_size()
    return height

  def get_size(room):
    return room.size

  def get_center(room):
    width, height = room.get_size()
    x, y = room.cell or (0, 0)
    return (
      x + width // 2,
      y + height // 2 - (height + 1) % 2
    )

  def get_cells(room):
    cells = []
    col, row = room.cell or (0, 0)
    width, height = room.get_size()
    for y in range(height):
      for x in range(width):
        cells.append((x + col, y + row))
    return cells

  def get_edges(room):
    room_width, room_height = room.size
    left, top = room.cell
    right = left + room_width
    bottom = top + room_height

    edges = []
    for x in range(left, right):
      edges.append((x, top - 2))
      edges.append((x, top - 1))
      edges.append((x, bottom))
      edges.append((x, bottom + 1))

    for y in range(top, bottom):
      edges.append((left - 1, y))
      edges.append((right, y))

    return edges

  def get_border(room):
    left, top = room.cell
    right = left + room.get_width()
    bottom = top + room.get_height()

    edges = []
    for x in range(left - 1, right + 1):
      edges.append((x, top - 2))
      edges.append((x, top - 1))
      edges.append((x, bottom))

    for y in range(top, bottom):
      edges.append((left - 1, y))
      edges.append((right, y))

    return edges

  def validate(room, cell, slots):
    cells = [add(c, cell) for c in room.get_cells()]
    cells = [(x, y) for x, y in cells if x % 2 == 1 and y % 3 == 1]
    for cell in cells:
      if cell not in slots:
        return False
    return True

  def filter_slots(room, slots):
    return [s for s in slots if room.validate(s, slots)]
