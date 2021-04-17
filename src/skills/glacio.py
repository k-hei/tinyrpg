from skills import Skill
from anims.attack import AttackAnim
from anims.pause import PauseAnim
import math
from actors.mage import Mage

ATTACK_DURATION = 12

class Glacio(Skill):
  name = "Glacio"
  kind = "spell"
  element = "ice"
  desc = "Freezes target with ice"
  cost = 3
  radius = math.inf
  users = (Mage,)
  blocks = (
    (0, 0),
    (1, 0)
  )

  def effect(game, on_end=None):
    game.log.print("But nothing happened...")
