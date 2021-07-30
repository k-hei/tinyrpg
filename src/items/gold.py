from items import Item
from comps.log import Token
from colors.palette import GOLD

class Gold(Item):
  name = "Gold"
  color = GOLD

  def __init__(item, amount):
    item.amount = amount

  def token(item):
    return Token(
      text="{amount}G".format(amount=item.amount),
      color=GOLD
    )
