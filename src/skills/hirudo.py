from skills import Skill
from anims.attack import AttackAnim
from anims.pause import PauseAnim
import math
from actors.mage import Mage

ATTACK_DURATION = 12

class Hirudo(Skill):
  name = "Hirudo"
  kind = "ailment"
  element = "dark"
  desc = "Drains target's HP"
  cost = 6
  users = (Mage,)
  blocks = (
    (0, 0),
    (1, 0),
    (0, 1),
    (1, 1)
  )

  def effect(user, game, on_end=None):
    game.log.print("But nothing happened...")
