from skills.armor import Armor
from cores import Core
from cores.knight import KnightCore as Knight
from cores.mage import Mage

class HpUp(Armor):
  hp = 5
  name = "HP +5"
  desc = "Increases HP by 5"
  users = (Knight, Mage)
