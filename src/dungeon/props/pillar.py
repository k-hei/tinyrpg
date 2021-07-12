from dungeon.element import DungeonElement
from assets import load as use_assets
from filters import replace_color
from colors.palette import WHITE, SAFFRON
from sprite import Sprite

class Pillar(DungeonElement):
  def view(pillar, anims):
    return super().view(Sprite(
      image=replace_color(use_assets().sprites["pillar"], WHITE, SAFFRON),
      layer="elems"
    ), anims)
