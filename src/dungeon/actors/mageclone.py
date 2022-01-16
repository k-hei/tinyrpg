from dungeon.actors import DungeonActor
from cores import Core, Stats
from cores.mage import Mage
from helpers.mage import step_move, view_mage
import assets
from lib.sprite import Sprite

from anims.shake import ShakeAnim

class MageClone(DungeonActor):

  class ChargeAnim(ShakeAnim): pass

  def __init__(mage, *args, **kwargs):
    super().__init__(Core(
      name="Minxia",
      faction="enemy",
      stats=Stats(
        hp=1,
        st=14,
        ma=14,
        dx=9,
        ag=7,
        lu=9,
        en=10,
      ),
    ), *args, **kwargs)
    mage.core.anims = [Mage.IdleDownAnim()]

  def step(mage, game):
    return step_move(mage, game)

  def view(mage, anims):
    return view_mage(mage, anims)
