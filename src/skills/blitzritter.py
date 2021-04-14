from skills import Skill
from anims.attack import AttackAnim
from anims.pause import PauseAnim
from anims.attack import AttackAnim
from config import ATTACK_DURATION

class Blitzritter(Skill):
  def __init__(skill):
    super().__init__(
      name="Blitzritter",
      kind="lance",
      element=None,
      desc="Pierces two squares ahead",
      cost=4,
      radius=2
    )

  def effect(skill, game, on_end=None):
    camera = game.camera
    floor = game.floor
    user = game.hero
    hero_x, hero_y = user.cell
    delta_x, delta_y = user.facing
    target_cell = (hero_x + delta_x, hero_y + delta_y)
    target_a = floor.get_actor_at(target_cell)
    target_b = floor.get_actor_at((hero_x + delta_x * 2, hero_y + delta_y * 2))

    def end_bump():
      if not target_a and not target_b:
        return game.anims[0].append(PauseAnim(
          duration=45,
          on_end=lambda: (
            game.log.print("But nothing happened..."),
            on_end and on_end()
          )
        ))

      atk = user.st + 1

      if target_a and target_b:
        return game.flinch(
          target=target_a,
          damage=atk,
          on_end=lambda: (game.flinch(
            target=target_b,
            damage=atk,
            on_end=on_end
          ))
        )

      target = target_a or target_b
      game.flinch(
        target=target,
        damage=atk,
        on_end=on_end
      )

    game.anims.append([AttackAnim(
      duration=ATTACK_DURATION,
      target=user,
      src_cell=user.cell,
      dest_cell=target_cell,
      on_end=end_bump
    )])

    return target_cell
