from skills import Skill
from anims.attack import AttackAnim
from anims.pause import PauseAnim
import math
from dungeon.actors.mage import Mage

ATTACK_DURATION = 12

class Ignis(Skill):
  name = "Ignis"
  kind = "magic"
  element = "fire"
  desc = "Burns target with flame"
  cost = 2
  range_max = 4
  users = (Mage,)
  blocks = (
    (0, 0),
    (0, 1)
  )

  def effect(user, game, on_end=None):
    game.log.print("But nothing happened...")
