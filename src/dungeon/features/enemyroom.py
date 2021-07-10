from random import randrange
from dungeon.features.specialroom import SpecialRoom
from dungeon.props.chest import Chest
from dungeon.actors.eye import Eye as Eyeball

class EnemyRoom(SpecialRoom):
  def __init__(room):
    room_width = 5
    room_height = 4
    super().__init__(
      degree=2,
      shape=[("." * room_width) for _ in range(room_height)],
      elems=[((randrange(room_width), randrange(room_height)), Eyeball()) for _ in range(2)]
    )

  def get_edges(room):
    room_width, room_height = room.get_size()
    room_x, room_y = room.cell
    return [(x, y) for (x, y) in super().get_edges() if (
      x == room_x + room_width // 2
      or y == room_y + room_height // 2
    )]
