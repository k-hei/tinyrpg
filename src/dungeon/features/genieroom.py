from dungeon.features.specialroom import SpecialRoom
from dungeon.props.door import Door

class GenieRoom(SpecialRoom):
  def __init__(room, *args, **kwargs):
    super().__init__(degree=2, shape=[
      "#·····#",
      " ····· ",
      " ····· ",
      " ····· ",
      " .../· ",
      ".......",
      ".......",
    ], *args, **kwargs)

  def get_edges(room):
    room_width, room_height = room.get_size()
    room_x, room_y = room.cell or (0, 0)
    return [
      # (room_x + room_width // 2, room_y - 1),
      (room_x + room_width // 2, room_y + room.get_height())
    ]

  def place(room, stage, *args, **kwargs):
    super().place(stage, *args, **kwargs)
    room_width, room_height = room.get_size()
    room_x, room_y = room.cell or (0, 0)
    top_edge = (room_x + room_width // 2, room_y - 1)
    stage.set_tile_at(top_edge, stage.DOOR_WAY)
    stage.spawn_elem_at(top_edge, Door())
