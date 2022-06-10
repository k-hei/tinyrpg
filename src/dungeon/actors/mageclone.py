from random import randint

from dungeon.actors import DungeonActor
from cores import Core, Stats
from cores.mage import Mage as MageCore
from dungeon.actors.mage import Mage
from helpers.mage import step_move

from anims.flicker import FlickerAnim
from anims.shake import ShakeAnim

class MageClone(DungeonActor):
  expires = True

  class ChargeAnim(ShakeAnim): pass

  def __init__(mage, faction="enemy", *args, **kwargs):
    super().__init__(Core(
      name="Minxia",
      faction=faction,
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
    mage.core.anims = [MageCore.IdleDownAnim()]

  def dissolve(mage, game):
    game.anims[-1].append(FlickerAnim(
      target=mage,
      duration=30,
      delay=randint(0, 30),
      on_end=lambda: mage in game.stage.elems and game.stage.remove_elem(mage)
    ))

  def step(mage, game):
    return step_move(mage, game)

  def view(mage, anims):
    return Mage.view(mage, anims)
