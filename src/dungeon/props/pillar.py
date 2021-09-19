from random import randint
from dungeon.props import Prop
import assets
from sprite import Sprite
from filters import replace_color
from colors.palette import WHITE, SAFFRON

class Pillar(Prop):
  solid = True
  static = True

  def __init__(pillar, broken=False):
    super().__init__()
    pillar.broken = randint(0, 1)

  def view(pillar, anims):
    if pillar.broken:
      pillar_image = assets.sprites["pillar_broken"]
    else:
      pillar_image = assets.sprites["pillar"]
    pillar_image = replace_color(pillar_image, WHITE, SAFFRON)
    return super().view([Sprite(
      image=pillar_image,
      layer="elems"
    )], anims)
