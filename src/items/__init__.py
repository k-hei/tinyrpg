from dataclasses import dataclass
import assets
from filters import replace_color
from comps.log import Token
from colors.palette import BLACK

@dataclass
class Item:
  name: str
  desc: str
  value: int = 0
  sprite: str = None
  color: int = BLACK
  fragile: bool = False

  def token(item):
    return Token(item.name, item.color)

  def render(item):
    sprite_name = item.sprite or item.name.lower()
    sprite_key = "item_" + sprite_name
    sprite = assets.sprites[sprite_key if sprite_key in assets.sprites else "item_orb"]
    if item.color == BLACK:
      return sprite
    else:
      return replace_color(sprite, BLACK, item.color)
