from items import Item
from palette import GOLD

class Gold(Item):
  name = "Gold"
  color = GOLD

  def __init__(item, amount):
    item.amount = amount
