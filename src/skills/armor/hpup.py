from skills import Skill
from dungeon.actors.knight import Knight
from dungeon.actors.mage import Mage

class HpUp(Skill):
  hp = 5
  name = "HP +" + str(hp)
  kind = "passive"
  desc = "Increases HP by " + str(hp)
  users = (Knight, Mage)
