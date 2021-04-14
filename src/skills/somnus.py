from skills import Skill
from anims.attack import AttackAnim
from anims.pause import PauseAnim
from config import ATTACK_DURATION

class Somnus(Skill):
  def __init__(skill):
    super().__init__(
      name="Somnus",
      kind="spell",
      element="dark",
      desc="Lulls target to sleep",
      cost=6,
      radius=1
    )

  def effect(skill, game, on_end=None):
    user = game.hero
    source_cell = user.cell
    hero_x, hero_y = source_cell
    delta_x, delta_y = user.facing
    target_cell = (hero_x + delta_x, hero_y + delta_y)
    target_actor = game.floor.get_actor_at(target_cell)
    def on_attack_end():
      if target_actor:
        target_actor.asleep = True
        if target_actor.idle:
          target_actor.activate()
        game.log.print(target_actor.name.upper() + " fell asleep!")
        if on_end:
          on_end()
      else:
        game.anims[0].append(PauseAnim(
          duration=30,
          on_end=lambda: (
            game.log.print("But nothing happened..."),
            game.anims[0].append(PauseAnim(
              duration=45,
              on_end=on_end
            ))
          )
        ))
    game.anims.append([
      AttackAnim(
        duration=ATTACK_DURATION,
        target=user,
        src_cell=user.cell,
        dest_cell=target_cell,
        on_end=on_attack_end
      )
    ])
