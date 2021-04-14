from skills import Skill
from anims.pause import PauseAnim

ATTACK_DURATION = 12

class Counter(Skill):
  def __init__(skill):
    super().__init__(
      name="Counter",
      kind="shield",
      element=None,
      desc="Reflects one phys attack",
      cost=12,
      radius=0
    )

  def effect(skill, game, on_end=None):
    user = game.hero
    user.counter = True
    game.log.print(user.name.upper() + " stands ready.")
    game.anims.append([PauseAnim(
      duration=30,
      on_end=on_end
    )])
    return user.cell
