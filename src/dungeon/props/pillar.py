from pygame import Rect
from random import randint
from dungeon.props import Prop
import assets
import lib.vector as vector
from lib.sprite import Sprite
from lib.filters import replace_color
from colors.palette import WHITE, SAFFRON

class Pillar(Prop):
  solid = True
  static = True
  breakable = True

  def __init__(pillar, broken=None):
    super().__init__()
    pillar.broken = broken if broken is not None else not randint(0, 2)

  @property
  def rect(pillar):
    if pillar._rect is None and pillar.pos:
      pillar._rect = Rect(
        vector.subtract(pillar.pos, (8, 0)),
        (16, 16)
      )
    return pillar._rect

  def crush(pillar, *_):
    if pillar.broken:
      return
    pillar.broken = True

  def view(pillar, anims):
    if pillar.broken:
      pillar_image = assets.sprites["pillar_broken"]
    else:
      pillar_image = assets.sprites["pillar"]
    pillar_image = replace_color(pillar_image, WHITE, SAFFRON)
    return super().view([Sprite(
      image=pillar_image,
      pos=(0, 16),
      layer="elems",
      origin=Sprite.ORIGIN_BOTTOM,
    )], anims)
