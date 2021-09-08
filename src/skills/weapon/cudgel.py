from skills.weapon import Weapon
from cores.mage import Mage

class Cudgel(Weapon):
  name = "Cudgel"
  desc = "A rod that channels magic."
  element = "staff"
  cost = 1
  st = 1
  users = [Mage]
  blocks = (
    (0, 0),
    (1, 0),
    (1, 1),
  )
