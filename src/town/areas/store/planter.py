from town.topview.element import Element
from assets import load as use_assets
from sprite import Sprite

class Planter(Element):
  size = (16, 16)

  def view(planter):
    planter_image = use_assets().sprites["store_planter"]
    planter_sprite = Sprite(
      image=planter_image,
      pos=planter.pos,
      origin=("center", "bottom"),
      layer="elems"
    )
    planter_sprite.move((0, 8))
    return [planter_sprite]
