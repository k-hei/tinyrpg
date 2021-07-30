import random
from skills.attack import AttackSkill
from anims.attack import AttackAnim
from anims.pause import PauseAnim
from anims.attack import AttackAnim
from anims.frame import FrameAnim
from dungeon.actors import DungeonActor
from cores.knight import Knight as Knight
from vfx.impact import ImpactVfx
from config import ATTACK_DURATION, TILE_SIZE, ENABLED_COMBAT_LOG

class Blitzritter(AttackSkill):
  name = "Blitzritter"
  desc = "Pierces two squares ahead"
  element = "lance"
  cost = 4
  range_type = "linear"
  range_min = 1
  range_max = 2
  range_radius = 0
  users = (Knight,)
  blocks = (
    (1, 0),
    (0, 1),
    (1, 1),
    (0, 2)
  )

  def effect(user, dest, game, on_end=None):
    camera = game.camera
    floor = game.floor
    hero_x, hero_y = user.cell
    delta_x, delta_y = user.facing
    near_cell = (hero_x + delta_x, hero_y + delta_y)
    far_cell = (hero_x + delta_x * 2, hero_y + delta_y * 2)
    target_a = floor.get_elem_at(near_cell)
    target_b = floor.get_elem_at(far_cell)

    if not isinstance(target_a, DungeonActor):
      target_a = None
    if not isinstance(target_b, DungeonActor):
      target_b = None

    def connect():
      game.vfx.extend([
        ImpactVfx(cell=near_cell),
        ImpactVfx(cell=far_cell, delay=10),
      ])

    def end_pause():
      if target_a and target_b:
        return game.flinch(
          target=target_a,
          damage=game.find_damage(user, target_a, modifier=1.25),
          on_end=lambda: game.flinch(
            target=target_b,
            damage=game.find_damage(user, target_b, modifier=1.25),
            on_end=on_end
          )
        )
      target = target_a or target_b
      game.flinch(
        target=target,
        damage=game.find_damage(user, target, modifier=1.25),
        on_end=on_end
      )

    def end_bump():
      if not target_a and not target_b:
        return game.anims[0].append(PauseAnim(
          duration=45,
          on_end=lambda: (
            ENABLED_COMBAT_LOG and game.log.print("But nothing happened..."),
            on_end and on_end()
          )
        ))
      game.anims[0].append(PauseAnim(
        duration=45,
        on_end=end_pause
      ))

    game.anims.append([AttackAnim(
      duration=ATTACK_DURATION,
      target=user,
      src=user.cell,
      dest=near_cell,
      on_connect=connect,
      on_end=end_bump
    )])

    return near_cell
