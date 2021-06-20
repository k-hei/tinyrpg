from town.topview.element import Element
from assets import load as use_assets
from sprite import Sprite

class PotionStock(Element):
  size = (32, 16)
  rect_offset = (-8, -8)

  def view(stock):
    stock_image = use_assets().sprites["store_potionstock"]
    stock_sprite = Sprite(
      image=stock_image,
      pos=stock.pos,
      origin=("center", "bottom"),
      layer="elems"
    )
    stock_sprite.move((8, 8))
    return [stock_sprite]
