from dungeon.element import DungeonElement
import assets
from filters import replace_color
from colors.palette import WHITE, SAFFRON
from sprite import Sprite

class Pillar(DungeonElement):
  solid = True
  static = True

  def __init__(pillar, broken=False):
    super().__init__()
    pillar.broken = broken

  def view(pillar, anims):
    if pillar.broken:
      pillar_image = assets.sprites["pillar_broken"]
    else:
      pillar_image = assets.sprites["pillar"]
    pillar_image = replace_color(pillar_image, WHITE, SAFFRON)
    return super().view(Sprite(
      image=pillar_image,
      layer="elems"
    ), anims)
