from dungeon.features.room import Room

class VerticalRoom(Room):
  def __init__(room, size, degree=0, secret=False):
    super().__init__(size, degree, secret)

  def get_exits(room):
    _, room_y = room.cell or (0, 0)
    center_x, _ = room.get_center()
    return [(x, y) for x, y in room.get_edges() if y == room_y - 1]
