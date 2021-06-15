from town.topview.element import Element
from assets import load as use_assets
from sprite import Sprite
from config import TILE_SIZE
from filters import replace_color
from palette import WHITE, BLUE_DARK

class FortuneStand(Element):
  size = (16, 16)

  def view(stand, sprites):
    stand_image = use_assets().sprites["fortune_stand"]
    stand_image = replace_color(stand_image, WHITE, BLUE_DARK)
    stand_sprite = Sprite(
      image=stand_image,
      pos=stand.pos,
      origin=("center", "bottom"),
      layer="elems"
    )
    stand_sprite.move((0, TILE_SIZE / 4))
    sprites.append(stand_sprite)
