from dungeon.element import DungeonElement
from assets import load as use_assets
from filters import replace_color
from palette import WHITE, GOLD
from sprite import Sprite

class Altar(DungeonElement):
  def __init__(altar):
    super().__init__()

  def view(altar, anims):
    assets = use_assets()
    altar_image = assets.sprites["altar"]
    altar_image = replace_color(altar_image, WHITE, GOLD)
    return super().view(Sprite(
      image=altar_image,
      layer="elems"
    ), anims)
