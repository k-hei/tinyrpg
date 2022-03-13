from cores.knight import Knight
from skills.support import SupportSkill
from dungeon.status.atk import AtkUpEffect

import debug

class Empower(SupportSkill):
  name = "Empower"
  desc = "Increases attack strength"
  element = "sword"
  cost = 4
  range_min = 0
  range_max = 0
  users = (Knight),
  blocks = [
    (0, 0),
    (1, 0),
    (0, 1),
  ]

  def effect(game, user, dest=None, on_start=None, on_end=None):
    user.apply_status_effect(AtkUpEffect())
    debug.log("atk up")
