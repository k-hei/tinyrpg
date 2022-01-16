from math import pi, inf
from skills.magic import MagicSkill
from anims.pause import PauseAnim
from cores.mage import Mage
from vfx.mageclone import MageCloneVfx

class Roulette(MagicSkill):
  name = "Illusion"
  desc = "Calls allies to your side"
  element = "shield"
  cost = 12
  range_min = 1
  range_max = 2
  range_type = "radial"
  charge_turns = 1
  users = [Mage]
  blocks = (
    (0, 0),
    (0, 1),
    (1, 0),
    (1, 1),
  )

  def effect(game, user, dest=None, on_start=None, on_end=None):
    on_start and on_start(user.cell)
    user.core.anims.append(Mage.CastAnim())
    game.darken()
    game.vfx.extend([
      MageCloneVfx(cell=user.cell, color=user.color(), angle=pi * 0),
      MageCloneVfx(cell=user.cell, color=user.color(), angle=pi * 0.5),
      MageCloneVfx(cell=user.cell, color=user.color(), angle=pi * 1),
      MageCloneVfx(cell=user.cell, color=user.color(), angle=pi * 1.5),
    ])
    game.anims.append([PauseAnim(duration=inf)])
    #   [PauseAnim(duration=90, on_end=lambda: (
    #     user.core.anims.pop(),
    #     game.undarken(),
    #     on_end and on_end(),
    #   ))],
    # ])
    return False
