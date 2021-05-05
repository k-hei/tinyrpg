from skills.magic import MagicSkill
from anims.attack import AttackAnim
from anims.pause import PauseAnim
from cores.mage import Mage
from vfx.fireball import Fireball
from config import TILE_SIZE

ATTACK_DURATION = 12

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

  def effect(user, dest, game, on_end=None):
    user_col, user_row = user.cell
    dest_col, dest_row = dest
    start = user_col * TILE_SIZE, user_row * TILE_SIZE
    target = dest_col * TILE_SIZE, dest_row * TILE_SIZE
    for i in range(6):
      delay = i * 7
      fireball = Fireball(start, target, delay)
      game.vfx.append(fireball)
    mid_x = (dest_col + user_col) / 2
    mid_y = (dest_row + user_row) / 2
    return (mid_x, mid_y)
