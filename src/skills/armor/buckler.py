from skills.armor import Armor
from cores import Core
from cores.knight import Knight

class Buckler(Armor):
  name = "Buckler"
  desc = "A small round shield"
  element = "shield"
  st = 1
  users = [Knight]
  blocks = [
    (0, 0),
    (1, 0),
    (0, 1),
    (1, 1),
  ]
