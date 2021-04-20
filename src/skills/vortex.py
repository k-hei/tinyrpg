from skills import Skill
from anims.attack import AttackAnim
from anims.pause import PauseAnim
import math
from actors.mage import Mage

ATTACK_DURATION = 12

class Vortex(Skill):
  name = "Vortex"
  kind = "magic"
  element = "wind"
  desc = "Drives target back with wind"
  cost = 3
  range_max = math.inf
  users = (Mage,)
  blocks = (
    (1, 0),
    (0, 1),
    (1, 1)
  )

  def effect(game, on_end=None):
    game.log.print("But nothing happened...")
