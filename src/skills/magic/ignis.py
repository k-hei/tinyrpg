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

  def effect(user, game, on_end=None):
    game.log.print("But nothing happened...")
    # game.vfx.append()
    col, row = user.cell
    x, y = col * TILE_SIZE, row * TILE_SIZE
    Fireball(
      start=(x, y),
      target=(0, 0)
    )
