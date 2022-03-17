from cores.knight import Knight
from skills.support import SupportSkill
from dungeon.status.defense import DefUpEffect
from vfx.def_up import DefUpVfx
from anims.pause import PauseAnim

import debug

class Fortify(SupportSkill):
  name = "Fortify"
  desc = "Boosts phys defense"
  element = "shield"
  cost = 3
  range_min = 0
  range_max = 0
  users = (Knight),
  blocks = [
    (1, 0),
    (0, 1),
    (1, 1),
  ]

  def effect(game, user, dest=None, on_start=None, on_end=None):
    game.anims.append([(pause_anim := PauseAnim(
      on_start=lambda: (
        game.vfx.append(DefUpVfx(cell=user.cell, on_end=pause_anim.end)),
        user.apply_status_effect(DefUpEffect()),
        user.core.anims.append(user.core.ChargeAnim()),
        on_start and on_start(),
      ),
      on_end=lambda: (
        user.core.anims.pop(),
        on_end and on_end(),
      ),
    ))])
