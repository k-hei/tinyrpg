from pygame import Surface, Rect, SRCALPHA
from pygame.transform import flip
import lib.vector as vector
from lib.filters import replace_color
from colors.palette import WHITE, SAFFRON

import assets
from lib.sprite import Sprite
from dungeon.props import Prop
from config import TILE_SIZE

assets.sprites["table_right"] = flip(assets.sprites["table_left"], True, False)

class Table(Prop):
  def __init__(table, length=1, *args, **kwargs):
    super().__init__(size=(length, 1), solid=True, *args, **kwargs)
    table.length = length

  @property
  def rect(table):
    if table._rect is None and table.pos:
      table._rect = Rect(
        vector.subtract(table.pos, (16, 16)),
        (table.length * 32, 32)
      )
    return table._rect

  def view(table, anims):
    table_width = TILE_SIZE * table.length
    table_image = Surface((table_width, TILE_SIZE), SRCALPHA)
    for x in range(assets.sprites["table_left"].get_width(), table_width - assets.sprites["table_right"].get_width(), assets.sprites["table_middle"].get_width()):
      table_image.blit(assets.sprites["table_middle"], (x, 0))
    table_image.blit(assets.sprites["table_left"], (0, 0))
    table_image.blit(assets.sprites["table_right"], (table_width - assets.sprites["table_right"].get_width(), 0))

    table_image = replace_color(table_image, WHITE, table.color)

    return super().view([Sprite(
      image=table_image,
      pos=((table_width - TILE_SIZE) / 2, 0),
      layer="elems"
    )], anims)
