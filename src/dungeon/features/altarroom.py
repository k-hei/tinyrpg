from dungeon.features.specialroom import SpecialRoom
from dungeon.props.altar import Altar

class AltarRoom(SpecialRoom):
  def __init__(room, *args, **kwargs):
    super().__init__(degree=2, shape=[
      ".......",
      "       ",
      " ..... ",
      " ..... ",
      " ..... ",
      " ..... ",
      " ..... ",
      "   .   ",
      "   .   ",
      "   .   ",
      "   .   ",
    ], elems=[
      ((3, 4), Altar())
    ], *args, **kwargs)
    room.entered = False

  def get_edges(room):
    room_width, room_height = room.get_size()
    room_x, room_y = room.cell or (0, 0)
    return [
      (room_x + room_width // 2, room_y + room.get_height())
    ]
