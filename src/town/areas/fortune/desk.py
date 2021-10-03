from town.topview.element import Element
from assets import load as use_assets
from lib.sprite import Sprite
from config import TILE_SIZE
from lib.filters import replace_color
from colors.palette import WHITE, ORANGE

class FortuneDesk(Element):
  size = (80, 16)
  spawn_offset = (0, 0)
  rect_offset = (-8, -8)
  draw_offset = (-8, 8)

  def view(desk):
    desk_image = use_assets().sprites["fortune_desk"]
    desk_image = replace_color(desk_image, WHITE, ORANGE)
    desk_sprite = Sprite(
      image=desk_image,
      pos=desk.pos,
      origin=("left", "bottom"),
      layer="elems"
    )
    desk_sprite.move(desk.draw_offset)
    return [desk_sprite]
