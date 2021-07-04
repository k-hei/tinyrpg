from dungeon.actors import DungeonActor
from cores.knight import Knight as KnightCore
from palette import ORANGE
from anims.walk import WalkAnim

class GuardActor(DungeonActor):
  def __init__(guard, core=None, *args, **kwargs):
    super().__init__(core=core or KnightCore(color=ORANGE, *args, **kwargs))
    guard.core.anims = [WalkAnim(period=45)]

  def view(guard, anims):
    return super().view(guard.core.view(), anims)
