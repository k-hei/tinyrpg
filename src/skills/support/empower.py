from cores.knight import Knight
from skills.support import SupportSkill
from dungeon.status.attack import AtkUpEffect
from vfx.atk_up import AtkUpVfx
from anims.pause import PauseAnim

import debug

class Empower(SupportSkill):
  name = "Empower"
  desc = "Boosts phys attack"
  element = "sword"
  cost = 3
  range_min = 0
  range_max = 0
  users = (Knight),
  blocks = [
    (0, 0),
    (1, 0),
    (0, 1),
  ]

  def effect(game, user, dest=None, on_start=None, on_end=None):
    game.anims.append([(pause_anim := PauseAnim(
      on_start=lambda: (
        game.vfx.append(AtkUpVfx(cell=user.cell, on_end=pause_anim.end)),
        user.apply_status_effect(AtkUpEffect()),
        user.core.anims.append(user.core.ChargeAnim()),
        on_start and on_start(),
      ),
      on_end=lambda: (
        user.core.anims.pop(),
        on_end and on_end(),
      ),
    ))])
