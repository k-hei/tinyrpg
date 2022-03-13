from cores.knight import Knight
from skills.support import SupportSkill
from dungeon.status.atk import AtkUpEffect
from vfx.atkup import AtkUpVfx
from anims.pause import PauseAnim

import debug

class Empower(SupportSkill):
  name = "Empower"
  desc = "Increases attack strength"
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
    game.anims.append([PauseAnim(
      duration=45,
      on_start=lambda: (
        game.vfx.append(AtkUpVfx(cell=user.cell)),
        user.core.anims.append(user.core.ChargeAnim()),
        user.apply_status_effect(AtkUpEffect()),
        on_start and on_start(),
      ),
      on_end=lambda: (
        user.core.anims.pop(),
        on_end and on_end(),
      ),
    )])
    debug.log("atk up")
