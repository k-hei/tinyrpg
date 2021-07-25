from dungeon.element import DungeonElement
import assets
from filters import replace_color
from colors.palette import WHITE, SAFFRON
from sprite import Sprite

class Pillar(DungeonElement):
  static = True

  def view(pillar, anims):
    return super().view(Sprite(
      image=replace_color(assets.sprites["pillar"], WHITE, SAFFRON),
      layer="elems"
    ), anims)
