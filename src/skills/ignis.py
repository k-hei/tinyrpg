from skills import Skill
from anims.attack import AttackAnim
from anims.pause import PauseAnim
import math
from actors.mage import Mage

ATTACK_DURATION = 12

class Ignis:
  name = "Ignis"
  kind = "spell"
  element = "fire"
  desc = "Burns target with flame"
  cost = 3
  radius = math.inf
  users = (Mage,)
  blocks = (
    (0, 0),
    (0, 1)
  )

  def effect(game, on_end=None):
    game.log.print("But nothing happened...")
