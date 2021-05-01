import random
from dungeon.features.specialroom import SpecialRoom
from dungeon.props.chest import Chest
from skills.weapon.caladbolg import Caladbolg
from skills.weapon.longinus import Longinus
from skills.weapon.mjolnir import Mjolnir

weapons = (Caladbolg, Longinus, Mjolnir)

class TreasureRoom(SpecialRoom):
  def __init__(room):
    room.actors = [ Chest(random.choice(weapons)) ]
    room.shape = [
      "#     #",
      "   0   ",
      "  ...  ",
      "  ...  ",
      "  ...  ",
      "   .   ",
      "#  .  #"
    ]
    super().__init__(degree=1)

  def get_edges(room):
    x, y = room.cell or (0, 0)
    return [(x + room.get_width() // 2, y + room.get_height() + 1)]
