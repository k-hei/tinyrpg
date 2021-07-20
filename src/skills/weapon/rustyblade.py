from skills.weapon import Weapon
from cores.knight import Knight

class RustyBlade(Weapon):
  name = "RustyBlade"
  desc = "An old sword"
  element = "sword"
  cost = 1
  st = 1
  users = [Knight]
  blocks = (
    (0, 0),
    (1, 0),
    (1, 1),
  )
