from config import ATTACK_DURATION
from skills import Skill
from anims.attack import AttackAnim
from anims.pause import PauseAnim
from comps.damage import DamageValue
import palette
import random

from actors import Actor
from actors.mage import Mage

class Anastasis(Skill):
  name = "Anastatis"
  kind = "support"
  element = None
  desc = "Restores HP slightly"
  cost = 12
  users = (Mage,)
  blocks = (
    (0, 0),
    (1, 0),
    (0, 1),
    (1, 1),
  )

  def effect(game, on_end=None):
    user = game.hero
    game.log.print(user.name.upper() + " stands ready.")
    game.anims.append([PauseAnim(
      duration=30,
      on_end=on_end
    )])
    return user.cell
