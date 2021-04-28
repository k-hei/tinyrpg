from dataclasses import dataclass
from assets import load as use_assets
from filters import replace_color
from comps.log import Token
from palette import BLACK

@dataclass(frozen=True)
class Item:
  name: str
  desc: str
  color: tuple[int, int, int] = BLACK

  def token(item):
    return Token(item.name, item.color)

  def render(item):
    sprite = use_assets().sprites["item_" + item.name.lower()]
    if item.color == BLACK:
      return sprite
    else:
      return replace_color(sprite, BLACK, item.color)
