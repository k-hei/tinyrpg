from skills.weapon import Weapon
from cores.knight import Knight

class Stick(Weapon):
  name = "Stick"
  desc = "A makeshift weapon"
  element = "sword"
  cost = 1
  st = 2
  users = (Knight,)
  blocks = (
    (0, 0),
    (1, 0)
  )
