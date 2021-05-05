from skills.magic import MagicSkill
from anims.attack import AttackAnim
from anims.pause import PauseAnim
from cores.mage import Mage
from vfx.fireball import Fireball
from config import TILE_SIZE, ATTACK_DURATION
from dungeon.actors import DungeonActor

class Ignis(MagicSkill):
  name = "Ignis"
  kind = "magic"
  element = "fire"
  desc = "Burns target with flame"
  cost = 2
  range_max = 4
  users = (Mage,)
  blocks = (
    (0, 0),
    (1, 0),
  )
  SALVO_SIZE = 6
  SALVO_STAGGER = 7

  def effect(user, dest, game, on_end=None):
    user_col, user_row = user.cell
    dest_col, dest_row = dest
    start_pos = user_col * TILE_SIZE, user_row * TILE_SIZE
    target_pos = dest_col * TILE_SIZE, dest_row * TILE_SIZE
    target = game.floor.get_elem_at(dest)
    target = target if isinstance(target, DungeonActor) else None

    on_end = lambda: (
      game.flinch(
        target=target,
        damage=20,
        delayed=True
      )
    )

    for i in range(Ignis.SALVO_SIZE):
      delay = i * Ignis.SALVO_STAGGER
      fireball = Fireball(start_pos, target_pos, delay, on_end=(
        on_end if target and i == Ignis.SALVO_SIZE - 1 else None
      ))
      game.vfx.append(fireball)

    game.anims.append([AttackAnim(
      duration=ATTACK_DURATION,
      target=user,
      src_cell=user.cell,
      dest_cell=dest
    )])

    mid_x = (dest_col + user_col) / 2
    mid_y = (dest_row + user_row) / 2
    return (mid_x, mid_y)
