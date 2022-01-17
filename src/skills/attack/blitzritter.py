from skills.attack import AttackSkill
from anims.attack import AttackAnim
from anims.pause import PauseAnim
from anims.attack import AttackAnim
from dungeon.actors import DungeonActor
from cores.knight import Knight as Knight
from vfx.impact import ImpactVfx
from config import ATTACK_DURATION, ENABLED_COMBAT_LOG

class Blitzritter(AttackSkill):
  name = "Blitzritter"
  desc = "Pierces two squares ahead"
  element = "lance"
  cost = 2
  range_type = "linear"
  range_min = 1
  range_max = 2
  range_radius = 0
  users = [Knight]
  blocks = (
    (0, 0),
    (1, 0),
    (1, 1),
    (2, 1)
  )

  def effect(game, user, dest, on_start=None, on_end=None):
    camera = game.camera
    floor = game.stage
    hero_x, hero_y = user.cell
    delta_x, delta_y = user.facing
    near_cell = (hero_x + delta_x, hero_y + delta_y)
    far_cell = (hero_x + delta_x * 2, hero_y + delta_y * 2)
    target_a = next((e for e in floor.get_elems_at(near_cell) if isinstance(e, DungeonActor)), None)
    target_b = next((e for e in floor.get_elems_at(far_cell) if isinstance(e, DungeonActor)), None)

    def connect():
      game.vfx.extend([
        ImpactVfx(cell=near_cell),
        ImpactVfx(cell=far_cell, delay=10),
      ])

    def end_pause():
      attack = lambda target, on_end: game.attack(
        actor=user,
        target=target,
        modifier=1.25,
        animate=False,
        # is_ranged=True,
        on_end=on_end
      )
      if target_a and target_b:
        attack(target=target_b, on_end=lambda: attack(target=target_a, on_end=on_end))
      elif target_a and not target_b:
        attack(target=target_a, on_end=on_end)
      elif not target_a and target_b:
        attack(target=target_b, on_end=on_end)
      elif not target_a and not target_b:
        on_end()

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
      on_start=lambda: on_start and on_start(),
      on_connect=connect,
      on_end=end_bump
    )])

    return near_cell
