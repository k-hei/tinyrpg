from town.topview.element import Element
from assets import load as use_assets
from sprite import Sprite
from config import TILE_SIZE
from filters import replace_color
from palette import WHITE, ORANGE

class FortuneDesk(Element):
  def __init__(desk, solid=False):
    super().__init__(solid=solid)

  def view(desk):
    desk_image = use_assets().sprites["fortune_desk"]
    desk_image = replace_color(desk_image, WHITE, ORANGE)
    desk_sprite = Sprite(
      image=desk_image,
      pos=desk.pos,
      origin=("left", "bottom"),
      layer="elems"
    )
    desk_sprite.move((-TILE_SIZE / 2, TILE_SIZE / 2))
    return [desk_sprite]
