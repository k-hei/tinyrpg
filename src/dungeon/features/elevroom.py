from dungeon.features.specialroom import SpecialRoom
from dungeon.stage import Stage
from dungeon.actors.eye import Eyeball
from assets import load as use_assets
from sprite import Sprite
from config import TILE_SIZE
from random import randint, choice
from filters import replace_color

class ElevRoom(SpecialRoom):
  def __init__(room, *args, **kwargs):
    super().__init__(
      degree=1,
      shape=[
        "·····\\.",
        "·····..",
        "·-···..",
        ".../·..",
        "...··..",
        ".......",
        "......."
      ],
      elems=[
        ((2, 0), Eyeball())
      ],
      *args, **kwargs
    )

  def get_edges(room):
    room_width, room_height = room.get_size()
    room_x, room_y = room.cell or (0, 0)
    return [(x, y) for (x, y) in super().get_edges() if y == room_y + room_height]
