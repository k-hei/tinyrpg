from skills import Skill
from anims.pause import PauseAnim

ATTACK_DURATION = 12

class Counter:
  name = "Counter"
  kind = "defense"
  element = "shield"
  desc = "Reflects phys damage"
  cost = 6
  radius = 0

  def effect(game, on_end=None):
    user = game.hero
    user.counter = 2
    game.log.print(user.name.upper() + " stands ready.")
    game.anims.append([PauseAnim(
      duration=30,
      on_end=on_end
    )])
    return user.cell
