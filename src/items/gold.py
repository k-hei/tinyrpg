from random import randint

from dataclasses import dataclass
from items import Item
from comps.log import Token
from colors.palette import BLACK, GOLD

from lib.filters import replace_color
import assets


@dataclass
class Gold(Item):
  name: str = "Gekkel"
  desc: str = "Standard Akimor currency."
  color: tuple = GOLD
  amount: int = 0

  def __post_init__(item):
    item.name = f"Gekkel ({item.amount}G)"
    item.amount = item.amount or randint(4, 30)

  def token(item):
    return Token(
      text="{amount}G".format(amount=item.amount),
      color=GOLD
    )

  def render(item):
    return replace_color(assets.sprites["item_gold"], BLACK, item.color)
