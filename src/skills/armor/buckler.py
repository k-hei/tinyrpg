from skills.armor import Armor
from cores import Core
from cores.knight import Knight
import assets
from filters import replace_color
from colors.palette import BLACK, ORANGE

class Buckler(Armor):
  name = "Buckler"
  desc = "A small round shield"
  element = "shield"
  st = 1
  en = 3
  users = [Knight]
  blocks = [
    (0, 0),
    (1, 0),
    (0, 1),
    (1, 1),
  ]

  def render(item=None):
    return replace_color(assets.sprites["item_shield"], BLACK, ORANGE)
