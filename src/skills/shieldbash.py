import math
from skills import Skill
from actors import Actor
from actors.eye import Eye
from actors.chest import Chest
from anims.move import MoveAnim
from anims.attack import AttackAnim
from anims.pause import PauseAnim
from anims.flicker import FlickerAnim
from config import ATTACK_DURATION, MOVE_DURATION

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
    user = game.hero
    floor = game.floor
    camera = game.camera

    source_cell = user.cell
    hero_x, hero_y = source_cell
    delta_x, delta_y = user.facing
    target_cell = (hero_x + delta_x, hero_y + delta_y)
    target_actor = floor.get_actor_at(target_cell)
    target_actor = None if type(target_actor) is Chest else target_actor

    if target_actor:
      # nudge target actor 1 square in the given direction
      target_x, target_y = target_cell
      nudge_cell = (target_x + delta_x, target_y + delta_y)
      nudge_tile = floor.get_tile_at(nudge_cell)
      nudge_actor = floor.get_actor_at(nudge_cell)
      will_nudge = (
        (not nudge_tile.solid or nudge_tile.pit)
        and nudge_actor is None
      )

      def on_move():
        target_actor.cell = nudge_cell
        if nudge_tile.pit:
          game.log.print(target_actor.name.upper() + " tumbles into the chasm below!")
          game.anims[0].append(FlickerAnim(
            duration=30,
            target=target_actor,
            on_end=lambda: game.floor.actors.remove(target_actor)
          ))
        else:
          game.log.print(target_actor.name.upper() + " is reeling.")

      def on_connect():
        if will_nudge:
          target_actor.stun = True
          game.anims[0].append(MoveAnim(
            duration=MOVE_DURATION,
            target=target_actor,
            src_cell=target_cell,
            dest_cell=nudge_cell,
            on_end=on_move
          ))

      game.attack(
        actor=user,
        target=target_actor,
        damage=math.ceil(Actor.find_damage(user, target_actor) / 2),
        on_connect=on_connect,
        on_end=on_end
      )
    else:
      game.anims.append([
        AttackAnim(
          duration=ATTACK_DURATION,
          target=user,
          src_cell=user.cell,
          dest_cell=target_cell,
          on_end=lambda: (game.anims[0].append(PauseAnim(
            duration=45,
            on_end=lambda: (
              game.log.print("But nothing happened..."),
              on_end and on_end()
            )
          )))
        )
      ])

    return target_cell
