from cores.knight import Knight
from skills.support import SupportSkill

class Empower(SupportSkill):
  name = "Empower"
  desc = "Temporarily increases attack strength"
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
    user.buff_atk()
