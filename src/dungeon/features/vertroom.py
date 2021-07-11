from dungeon.features.room import Room

class VerticalRoom(Room):
  def __init__(room, *args, **kwargs):
    super().__init__(*args, **kwargs)

  def get_exits(room):
    _, room_y = room.cell or (0, 0)
    center_x, _ = room.get_center()
    return [(x, y) for x, y in super().get_edges() if y == room_y - 1]

  def get_edges(room):
    _, room_y = room.cell or (0, 0)
    center_x, _ = room.get_center()
    return [(x, y) for x, y in super().get_edges() if y > room_y - 1]
