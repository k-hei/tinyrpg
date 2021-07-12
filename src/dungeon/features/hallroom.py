from dungeon.features.specialroom import SpecialRoom
from dungeon.features.room import Room

class HallRoom(SpecialRoom):
  def __init__(feature):
    super().__init__(degree=2, shape=[
      "     .....     ",
      "     .....     ",
      "     .....     ",
      "       .       ",
      "       .       ",
      "       .       ",
      "       .       ",
      "       .       ",
      "       .       ",
      "       .       ",
      "       .       ",
      "       .       ",
      "       .       ",
      "       .       ",
      "       .       ",
      "       .       ",
      "     .....     ",
      "     .....     ",
      "     .....     "
    ])

  def get_edges(feature):
    x, y = feature.cell or (0, 0)
    return [
      (x + feature.get_width() // 2, y - 2),
      (x + feature.get_width() // 2, y - 1),
      (x + feature.get_width() // 2, y + feature.get_height()),
      (x + feature.get_width() // 2, y + feature.get_height() + 1),
    ]
