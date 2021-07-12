from config import ATTACK_DURATION
from skills.support import SupportSkill
from anims.attack import AttackAnim
from anims.pause import PauseAnim
from comps.damage import DamageValue
import random

from dungeon.actors import DungeonActor
from dungeon.actors.mage import Mage

class Anastasis(SupportSkill):
  name = "Anastasis"
  desc = "Restores HP slightly"
  element = None
  cost = 12
  users = (Mage,)
  blocks = (
    (0, 0),
    (1, 0),
    (0, 1),
    (1, 1),
  )

  def effect(user, game, on_end=None):
    game.log.print((user.token(), " stands ready."))
    game.anims.append([PauseAnim(
      duration=30,
      on_end=on_end
    )])
    return user.cell
