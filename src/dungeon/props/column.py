from pygame import Rect
import lib.vector as vector

from dungeon.props import Prop
import assets
from lib.sprite import Sprite
from lib.filters import replace_color
from colors.palette import WHITE, SAFFRON

class Column(Prop):
  solid = True
  static = True

  @property
  def rect(pillar):
    if pillar._rect is None and pillar.pos:
      pillar._rect = Rect(
        vector.subtract(pillar.pos, (8, 0)),
        (16, 16)
      )
    return pillar._rect

  def view(column, anims):
    column_image = assets.sprites["column"]
    column_image = replace_color(column_image, WHITE, SAFFRON)
    return super().view([Sprite(
      image=column_image,
      layer="elems"
    )], anims)
