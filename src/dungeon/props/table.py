from pygame import Surface
from pygame.transform import flip
from lib.filters import replace_color
from colors.palette import WHITE, SAFFRON

import assets
from lib.sprite import Sprite
from dungeon.props import Prop
from config import TILE_SIZE

assets.sprites["table_left"] = replace_color(assets.sprites["table_left"], WHITE, SAFFRON)
assets.sprites["table_middle"] = replace_color(assets.sprites["table_middle"], WHITE, SAFFRON)
assets.sprites["table_right"] = flip(assets.sprites["table_left"], True, False)

class Table(Prop):
  def __init__(table, length=1, *args, **kwargs):
    super().__init__(size=(length, 1), solid=True, *args, **kwargs)
    table.length = length

  def view(table, anims):
    table_width = TILE_SIZE * table.length
    table_image = Surface((table_width, TILE_SIZE))
    ends_width = assets.sprites["table_left"].get_width() + assets.sprites["table_right"].get_width()
    for x in range(assets.sprites["table_left"].get_width(), table_width - assets.sprites["table_right"].get_width(), assets.sprites["table_middle"].get_width()):
      table_image.blit(assets.sprites["table_middle"], (x, 0))
    table_image.blit(assets.sprites["table_left"], (0, 0))
    table_image.blit(assets.sprites["table_right"], (table_width - assets.sprites["table_right"].get_width(), 0))
    return super().view([Sprite(
      image=table_image,
      pos=((table_width - TILE_SIZE) / 2, 0),
      layer="elems"
    )], anims)
