from skills.weapon import Weapon
from cores.knight import KnightCore

class Stick(Weapon):
  name = "Stick"
  desc = "A makeshift weapon"
  element = "lance"
  cost = 1
  st = 2
  users = (KnightCore,)
  blocks = (
    (0, 0),
    (1, 0)
  )
