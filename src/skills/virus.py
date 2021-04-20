from skills import Skill
from anims.attack import AttackAnim
from anims.pause import PauseAnim
import math
from actors.mage import Mage

ATTACK_DURATION = 12

class Virus(Skill):
  name = "Virus"
  kind = "ailment"
  element = "dark"
  desc = "Poisons adjacent targets"
  cost = 4
  radius = 1
  radius_min = 1
  radius_max = 1
  radius_type = "radial"
  users = (Mage,)
  blocks = (
    (0, 0),
    (1, 0),
    (1, 1),
  )

  def effect(game, on_end=None):
    game.log.print("But nothing happened...")
