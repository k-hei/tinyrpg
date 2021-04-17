from skills import Skill
from anims.attack import AttackAnim
from anims.pause import PauseAnim

ATTACK_DURATION = 12

class Obscura:
  name = "Obscura"
  kind = "ailment"
  element = "dark"
  desc = "Blinds target with darkness"
  cost = 6
  radius = 1

  def effect(skill, game, on_end=None):
    game.log.print("But nothing happened...")
