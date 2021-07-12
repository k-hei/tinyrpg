from dungeon.features.specialroom import SpecialRoom
from dungeon.features.room import Room

class HallRoom(SpecialRoom):
  def __init__(feature):
    super().__init__(degree=2, shape=[
      "       .....       ",
      "       .....       ",
      "       .....       ",
      "         .         ",
      "         .         ",
      "         .         ",
      "         .         ",
      "         .         ",
      "         .         ",
      "         .         ",
      "         .         ",
      "         .         ",
      "         .         ",
      "         .         ",
      "         .         ",
      "         .         ",
      "       .....       ",
      "       .....       ",
      "       .....       "
    ])

  def get_edges(feature):
    x, y = feature.cell or (0, 0)
    return [
      (x + 9, y - 2),
      (x + 9, y - 1),
      (x + 9, y + feature.get_height()),
      (x + 9, y + feature.get_height() + 1),
    ]
