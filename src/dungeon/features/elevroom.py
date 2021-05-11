from dungeon.features.specialroom import SpecialRoom
from dungeon.stage import Stage
from assets import load as use_assets
from sprite import Sprite
from config import TILE_SIZE
from random import randint, choice
from palette import WHITE, COLOR_TILE
from filters import replace_color

class ElevRoom(SpecialRoom):
  def __init__(room, secret=False):
    room.shape = [
      "·····##",
      "····-..",
      "····-..",
      "·=··...",
      ".......",
      ".......",
      "......."
    ]
    super().__init__(degree=1, secret=secret)

  def get_edges(room):
    room_width, room_height = room.get_size()
    room_x, room_y = room.cell or (0, 0)
    return [(x, y) for (x, y) in super().get_edges() if y == room_y + room_height]
