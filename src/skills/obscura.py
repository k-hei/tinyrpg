from skills import Skill
from anims.attack import AttackAnim
from anims.pause import PauseAnim
from actors.mage import Mage

ATTACK_DURATION = 12

class Obscura:
  name = "Obscura"
  kind = "ailment"
  element = "dark"
  desc = "Blinds target with darkness"
  cost = 4
  radius = 1
  users = (Mage,)
  blocks = (
    (0, 0),
    (1, 0),
    (2, 0)
  )

  def effect(game, on_end=None):
    game.log.print("But nothing happened...")
