from dungeon.features.specialroom import SpecialRoom

class OasisRoom(SpecialRoom):
  def __init__(room, secret=False):
    room.shape = [
      "#...#",
      ".....",
      ".OOO.",
      ".OOO.",
      ".OOO.",
      ".....",
      "#...#"
    ]
    super().__init__(degree=1, secret=secret)

  def get_cells(room):
    return [c for c in super().get_cells() if c not in room.get_corners()]

  def get_border(room):
    return super().get_border() + room.get_corners()

  def get_edges(room):
    x, y = room.cell or (0, 0)
    width, height = room.size
    return [
      (x + width // 2, y - 1),
      (x + width // 2, y + height + 1),
      (x - 1, y + height // 2),
      (x + width, y + height // 2),
    ]
