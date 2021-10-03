from skills.weapon import Weapon
from cores.knight import Knight
from colors.palette import BLACK, GRAY
from lib.filters import replace_color
import assets

class BroadSword(Weapon):
  name = "BroadSword"
  desc = "A sword used by a hot chick"
  element = "sword"
  cost = 1
  st = 5
  users = [Knight]
  blocks = (
    (0, 0),
    (1, 0),
    (0, 1),
    (1, 1),
  )

  def render(item=None):
    return replace_color(assets.sprites["item_sword"], BLACK, GRAY)
