from contexts import Context
from savedata.resolve import resolve_item
import assets
from lib.sprite import Sprite

def view_item_sticky(item):
  sticky_image = assets.sprites["buy_sticky"]
  item_image = item().render()
  return [
    Sprite(image=sticky_image),
    Sprite(
      image=item_image,
      pos=(sticky_image.get_width() // 2, sticky_image.get_height() // 2),
      origin=("center", "center")
    ),
  ]

class BuyContext(Context):
  def __init__(ctx, *args, **kwargs):
    super().__init__(*args, **kwargs)
    ctx.items = ["Potion", "Ankh", "Fish", "Cheese"]
    ctx.items = [resolve_item(i) for i in ctx.items]

  def view(ctx):
    sprites = []
    for i, item in enumerate(ctx.items):
      item_sprites = view_item_sticky(item)
      for sprite in item_sprites:
        sprite.move((i * 24, 0))
      item_sprites[1].move((0, 1))
      sprites += item_sprites
    return sprites
