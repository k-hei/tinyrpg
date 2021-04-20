from skills import Skill
from anims.pause import PauseAnim
from actors.knight import Knight

ATTACK_DURATION = 12

class Counter(Skill):
  name = "Counter"
  kind = "support"
  element = "shield"
  desc = "Reflects phys damage"
  cost = 6
  range_min = 0
  range_max = 0
  users = (Knight,)
  blocks = (
    (0, 0),
    (1, 0)
  )

  def effect(game, on_end=None):
    user = game.hero
    user.counter = 2
    game.log.print(user.name.upper() + " stands ready.")
    game.anims.append([PauseAnim(
      duration=30,
      on_end=on_end
    )])
    return user.cell
