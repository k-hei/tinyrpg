from dungeon.actors import DungeonActor
from cores.ghost import Ghost as GhostCore
from skills.weapon.tackle import Tackle
from anims.move import MoveAnim
from anims.attack import AttackAnim
from anims.flinch import FlinchAnim
from anims.flicker import FlickerAnim
import assets

class Ghost(DungeonActor):
  def __init__(ghost, *args, **kwargs):
    super().__init__(GhostCore(
      skills=[Tackle]
    ), *args, **kwargs)

  def view(ghost, anims):
    ghost_image = assets.sprites["ghost"]
    anim_group = [a for a in anims[0] if a.target is ghost] if anims else []
    for anim in anim_group:
      if type(anim) in (MoveAnim, AttackAnim):
        ghost_image = assets.sprites["ghost_move"]
      elif type(anim) in (FlinchAnim, FlickerAnim):
        ghost_image = assets.sprites["ghost_flinch"]
    return ghost.core.view(
      sprites=super().view(ghost_image, anims),
      anims=anim_group
    )
