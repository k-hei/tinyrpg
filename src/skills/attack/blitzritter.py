from skills.attack import AttackSkill
from config import ATTACK_DURATION, TILE_SIZE
from anims.attack import AttackAnim
from anims.pause import PauseAnim
from anims.attack import AttackAnim
from anims.frame import FrameAnim
from dungeon.actors import DungeonActor
from cores.knight import Knight as Knight
from vfx import Vfx
import random

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
    print(target_a, target_b)

    if not isinstance(target_a, DungeonActor):
      target_a = None
    if not isinstance(target_b, DungeonActor):
      target_b = None

    def connect():
      near_col, near_row = near_cell
      near_x = near_col * TILE_SIZE
      near_y = near_row * TILE_SIZE
      near_pos = (near_x, near_y)

      far_col, far_row = far_cell
      far_x = far_col * TILE_SIZE
      far_y = far_row * TILE_SIZE
      far_pos = (far_x, far_y)

      impact_frames = [
        "fx_impact0",
        "fx_impact1",
        "fx_impact2",
        "fx_impact3",
        "fx_impact4",
        "fx_impact5",
        "fx_impact6"
      ]
      game.vfx.extend([
        Vfx(
          kind="impact",
          pos=near_pos,
          anim=FrameAnim(
            duration=20,
            frames=impact_frames
          )
        ),
        Vfx(
          kind="impact",
          pos=far_pos,
          anim=FrameAnim(
            duration=20,
            delay=10,
            frames=impact_frames
          )
        )
      ])

    def find_damage(target):
      en = target.core.en if not target.ailment == "sleep" else 0
      return int((user.core.st + user.weapon.st) * 1.25 - en) + random.randint(-2, 2)

    def end_pause():
      if target_a and target_b:
        return game.flinch(
          target=target_a,
          damage=find_damage(target_a),
          on_end=lambda: game.flinch(
            target=target_b,
            damage=find_damage(target_b),
            on_end=on_end
          )
        )
      target = target_a or target_b
      game.flinch(
        target=target,
        damage=find_damage(target),
        on_end=on_end
      )

    def end_bump():
      if not target_a and not target_b:
        return game.anims[0].append(PauseAnim(
          duration=45,
          on_end=lambda: (
            game.log.print("But nothing happened..."),
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
      src_cell=user.cell,
      dest_cell=near_cell,
      on_connect=connect,
      on_end=end_bump
    )])

    return near_cell
