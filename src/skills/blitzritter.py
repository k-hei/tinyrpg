from skills import Skill
from config import ATTACK_DURATION, TILE_SIZE
from anims.attack import AttackAnim
from anims.pause import PauseAnim
from anims.attack import AttackAnim
from anims.frame import FrameAnim
from actors.knight import Knight
from props.chest import Chest
from comps.vfx import Vfx
import random

class Blitzritter(Skill):
  name = "Blitzritter"
  kind = "attack"
  element = "lance"
  desc = "Pierces two squares ahead"
  cost = 4
  radius = 2
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

  def effect(user, game, on_end=None):
    camera = game.camera
    floor = game.floor
    hero_x, hero_y = user.cell
    delta_x, delta_y = user.facing
    near_cell = (hero_x + delta_x, hero_y + delta_y)
    far_cell = (hero_x + delta_x * 2, hero_y + delta_y * 2)
    target_a = floor.get_elem_at(near_cell)
    target_b = floor.get_elem_at(far_cell)

    # TODO: prevent chests from being recognized as actors
    if type(target_a) is Chest:
      target_a = None
    if type(target_b) is Chest:
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

      game.vfx.extend([
        Vfx(
          kind="impact",
          pos=near_pos,
          anim=FrameAnim(
            duration=20,
            frame_count=7
          )
        ),
        Vfx(
          kind="impact",
          pos=far_pos,
          anim=FrameAnim(
            duration=20,
            delay=10,
            frame_count=7
          )
        )
      ])

    def find_damage(target):
      en = target.en if not target.ailment == "sleep" else 0
      return int(user.st * 1.25 - en) + random.randint(-2, 2)

    def end_pause():
      if target_a and target_b:
        return game.flinch(
          target=target_a,
          damage=find_damage(target_a),
          on_end=lambda: (game.flinch(
            target=target_b,
            damage=find_damage(target_b),
            on_end=on_end
          ))
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
