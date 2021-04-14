from skills import Skill
from actors import Actor
from actors.eye import Eye
from anims.move import MoveAnim
from anims.attack import AttackAnim
import math

MOVE_DURATION = 16
ATTACK_DURATION = 12

class ShieldBash(Skill):
  def __init__(skill):
    super().__init__(
      name="Shield Bash",
      kind="shield",
      element=None,
      desc="Pushes target one square",
      cost=2,
      radius=1,
    )

  # TODO: move into separate skill
  def effect(skill, game, on_end=None):
    if game.sp >= skill.cost:
      game.sp -= skill.cost

    user = game.hero
    source_cell = user.cell
    hero_x, hero_y = source_cell
    delta_x, delta_y = user.facing
    target_cell = (hero_x + delta_x, hero_y + delta_y)
    target_actor = game.floor.get_actor_at(target_cell)
    game.log.print(user.name.upper() + " uses Shield Bash")

    if target_actor:
      # nudge target actor 1 square in the given direction
      target_x, target_y = target_cell
      nudge_cell = (target_x + delta_x, target_y + delta_y)
      nudge_tile = game.floor.get_tile_at(nudge_cell)
      nudge_actor = game.floor.get_actor_at(nudge_cell)
      will_nudge = not nudge_tile.solid and nudge_actor is None

      def on_connect():
        if will_nudge:
          target_actor.cell = nudge_cell
          game.anims[0].append(MoveAnim(
            duration=MOVE_DURATION,
            target=target_actor,
            src_cell=target_cell,
            dest_cell=nudge_cell
          ))
          game.log.print(target_actor.name.upper() + " is reeling.")

      game.attack(
        actor=user,
        target=target_actor,
        damage=math.ceil(Actor.find_damage(user, target_actor) / 2),
        on_connect=on_connect,
        on_end=on_end
      )
    else:
      game.log.print("But nothing happened...")
      game.anims.append([
        AttackAnim(
          duration=ATTACK_DURATION,
          target=user,
          src_cell=user.cell,
          dest_cell=target_cell,
          on_end=on_end
        )
      ])
