from dataclasses import dataclass
import math

from skills.attack import AttackSkill
from dungeon.actors import DungeonActor
from cores.knight import Knight
from dungeon.props import Prop
from anims.move import MoveAnim
from anims.attack import AttackAnim
from anims.pause import PauseAnim
from anims.flicker import FlickerAnim
from config import ENABLED_COMBAT_LOG

class ShieldBash(AttackSkill):
  name = "ShieldBash"
  desc = "Pushes target one square"
  element = "shield"
  cost = 2
  users = [Knight]
  blocks = (
    (0, 0),
    (1, 0),
    (1, 1),
    (1, 2),
  )

  def effect(user, dest, game, on_end=None):
    floor = game.floor
    camera = game.camera

    source_cell = user.cell
    hero_x, hero_y = source_cell
    delta_x, delta_y = user.facing
    target_cell = (hero_x + delta_x, hero_y + delta_y)
    target_elem = floor.get_elem_at(target_cell, superclass=DungeonActor)

    if target_elem is None:
      game.anims.append([
        AttackAnim(
          target=user,
          src=user.cell,
          dest=target_cell,
          on_end=lambda: game.anims[0].append(PauseAnim(
            duration=45,
            on_end=lambda: (
              ENABLED_COMBAT_LOG and game.log.print("But nothing happened..."),
              on_end and on_end()
            )
          ))
        )
      ])
      return target_cell

    # nudge target actor 1 square in the given direction
    target_x, target_y = target_cell
    nudge_cell = (int(target_x + delta_x), int(target_y + delta_y))
    nudge_tile = floor.get_tile_at(nudge_cell)
    nudge_actor = floor.get_elem_at(nudge_cell, superclass=DungeonActor)
    will_nudge = (
      (not nudge_tile.solid or nudge_tile is floor.PIT)
      and nudge_actor is None
    )

    def on_connect():
      if will_nudge:
        game.nudge(actor=target_elem, direction=user.facing)
      game.flinch(
        target=target_elem,
        damage=game.find_damage(actor=user, target=target_elem, modifier=0.8),
        on_end=on_end
      )
      if ENABLED_COMBAT_LOG:
        if nudge_tile is floor.PIT:
          game.log.print((target_elem.token(), " tumbles into the chasm below!"))
        else:
          game.log.print((target_elem.token(), " is reeling."))

    game.anims.append([
      AttackAnim(
        target=user,
        src=user.cell,
        dest=target_cell,
        on_connect=on_connect
      )
    ])
    return target_cell
