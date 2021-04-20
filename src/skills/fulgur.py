from skills import Skill
from anims.attack import AttackAnim
from anims.pause import PauseAnim
import math
from actors.mage import Mage

ATTACK_DURATION = 12

class Fulgur(Skill):
  name = "Fulgur"
  kind = "magic"
  element = "volt"
  desc = "Shocks target with lightning"
  cost = 3
  range_max = 4
  users = (Mage,)
  blocks = (
    (0, 0),
    (1, 0)
  )

  def effect(game, on_end=None):
    game.log.print("But nothing happened...")
