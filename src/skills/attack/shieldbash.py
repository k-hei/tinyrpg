from dataclasses import dataclass
import math

from skills.attack import AttackSkill
from dungeon.actors import DungeonActor
from dungeon.actors.knight import Knight
from dungeon.props import Prop
from anims.move import MoveAnim
from anims.attack import AttackAnim
from anims.pause import PauseAnim
from anims.flicker import FlickerAnim
from config import ATTACK_DURATION, MOVE_DURATION

class ShieldBash(AttackSkill):
  name = "ShieldBash"
  desc = "Pushes target one square"
  element = "shield"
  cost = 2
  users = (Knight,)
  blocks = (
    (1, 0),
    (0, 1),
    (1, 1),
  )

  def effect(user, dest, game, on_end=None):
    floor = game.floor
    camera = game.camera

    source_cell = user.cell
    hero_x, hero_y = source_cell
    delta_x, delta_y = user.facing
    target_cell = (hero_x + delta_x, hero_y + delta_y)
    target_elem = floor.get_elem_at(target_cell)
    target_elem = None if isinstance(target_elem, Prop) else target_elem

    if target_elem:
      # nudge target actor 1 square in the given direction
      target_x, target_y = target_cell
      nudge_cell = (target_x + delta_x, target_y + delta_y)
      nudge_tile = floor.get_tile_at(nudge_cell)
      nudge_actor = floor.get_elem_at(nudge_cell)
      will_nudge = (
        (not nudge_tile.solid or nudge_tile is floor.PIT)
        and nudge_actor is None
      )

      def on_move():
        if nudge_tile is floor.PIT:
          game.log.print((target_elem.token(), " tumbles into the chasm below!"))
        else:
          game.log.print((target_elem.token(), " is reeling."))

      def on_connect():
        if will_nudge:
          move.start()

      game.attack(
        actor=user,
        target=target_elem,
        damage=math.ceil(DungeonActor.find_damage(user, target_elem) / 2),
        on_end=on_end,
        on_connect=on_connect
      )
      if will_nudge:
        target_elem.cell = nudge_cell
        target_elem.stepped = True
        move = MoveAnim(
          duration=MOVE_DURATION,
          target=target_elem,
          src=target_cell,
          dest=nudge_cell,
          started=False,
          on_end=on_move
        )
        game.anims[-1].append(move)
    else:
      game.anims.append([
        AttackAnim(
          duration=ATTACK_DURATION,
          target=user,
          src=user.cell,
          dest=target_cell,
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
