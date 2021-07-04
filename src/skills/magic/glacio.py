from skills.magic import MagicSkill
from cores.mage import Mage

ATTACK_DURATION = 12

class Glacio(MagicSkill):
  name = "Glacio"
  kind = "magic"
  element = "ice"
  desc = "Freezes target with ice"
  cost = 4
  range_max = 4
  users = [Mage]
  blocks = (
    (0, 0),
    (1, 0),
  )

  def effect(user, dest, game, on_end=None):
    game.log.print("{}".format(dest))
