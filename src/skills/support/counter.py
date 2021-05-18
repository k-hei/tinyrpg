from skills.support import SupportSkill
from anims.pause import PauseAnim
from cores.knight import KnightCore

ATTACK_DURATION = 12

class Counter(SupportSkill):
  name = "Counter"
  desc = "Reflects phys damage"
  element = "shield"
  cost = 6
  range_min = 0
  range_max = 0
  users = (KnightCore,)
  blocks = (
    (0, 0),
    (0, 1)
  )

  def effect(user, dest, game, on_end=None):
    user.counter = 2
    game.log.print((user.token(), " stands ready."))
    game.anims.append([PauseAnim(
      duration=30,
      on_end=on_end
    )])
    return user.cell
