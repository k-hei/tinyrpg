from skills import Skill
from anims.attack import AttackAnim
from anims.pause import PauseAnim
import math
from dungeon.actors.mage import Mage

ATTACK_DURATION = 12

class Glacio(Skill):
  name = "Glacio"
  kind = "magic"
  element = "ice"
  desc = "Freezes target with ice"
  cost = 3
  range_max = 4
  users = (Mage,)
  blocks = (
    (0, 0),
    (1, 0)
  )

  def effect(user, game, on_end=None):
    game.log.print("But nothing happened...")
