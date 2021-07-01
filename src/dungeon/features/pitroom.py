from dungeon.features.specialroom import SpecialRoom

class PitRoom(SpecialRoom):
  def __init__(room, secret=False):
    super().__init__(degree=2, secret=secret, shape=[
      ". . .",
      "     ",
      ". . .",
      "     ",
      ". . .",
      "     ",
      ". . ."
    ])

  def get_edges(room):
    edges = super().get_edges()
    room_x, room_y = room.cell or (0, 0)
    room_width, room_height = room.size
    return [(x, y) for (x, y) in edges if (
      (y == room_y - 1 or y == room_y + room_height - 1) and x % 2 == 1
      or (x == room_x - 1 or x == room_x + room_width - 1) and y % 2 == 1
    )]
