from skills.support import SupportSkill
from anims.pause import PauseAnim
from dungeon.actors.knight import Knight

ATTACK_DURATION = 12

class Counter(SupportSkill):
  name = "Counter"
  desc = "Reflects phys damage"
  element = "shield"
  cost = 6
  range_min = 0
  range_max = 0
  users = (Knight,)
  blocks = (
    (1, 0),
    (0, 1),
    (1, 1)
  )

  def effect(user, game, on_end=None):
    user.counter = 2
    game.log.print((user.token(), " stands ready."))
    game.anims.append([PauseAnim(
      duration=30,
      on_end=on_end
    )])
    return user.cell
