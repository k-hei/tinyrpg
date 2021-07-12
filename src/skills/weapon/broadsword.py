from skills.weapon import Weapon
from cores.knight import Knight

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
