from skills import Skill
from anims.attack import AttackAnim
from anims.pause import PauseAnim
import math

ATTACK_DURATION = 12

class Ignis:
  name = "Ignis"
  kind = "spell"
  element = "fire"
  desc = "Burns target with flame"
  cost = 3
  radius = math.inf

  def effect(skill, game, on_end=None):
    game.log.print("But nothing happened...")
