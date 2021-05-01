from dungeon.features.room import Room

class OasisRoom(Room):
  def __init__(room, secret=False):
    super().__init__((5, 7), degree=1, secret=secret)

  def get_cells(room):
    x, y = room.cell or (0, 0)
    width, height = room.size
    corners = [
      (x, y),
      (x + width - 1, y),
      (x, y + height - 1),
      (x + width - 1, y + height - 1),
    ]
    cells = super().get_cells()
    for c in corners:
      cells.remove(c)
    return cells

  def get_edges(room):
    x, y = room.cell or (0, 0)
    width, height = room.size
    return [
      (x + width // 2, y - 1),
      (x + width // 2, y + height + 1),
      (x - 1, y + height // 2),
      (x + width, y + height // 2),
    ]
