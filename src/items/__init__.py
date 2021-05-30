from dataclasses import dataclass
from assets import load as use_assets
from filters import replace_color
from comps.log import Token
from palette import BLACK

@dataclass
class Item:
  name: str
  desc: str
  value: int = 0
  sprite: str = None
  color: tuple[int, int, int] = BLACK

  def token(item):
    return Token(item.name, item.color)

  def render(item):
    sprite_name = item.sprite or item.name.lower()
    sprite = use_assets().sprites["item_" + sprite_name]
    if item.color == BLACK:
      return sprite
    else:
      return replace_color(sprite, BLACK, item.color)
