from random import randint

from dungeon.actors import DungeonActor
from dungeon.actors.mage import Mage
from cores import Core, Stats
from cores.mage import Mage as MageCore
from helpers.mage import step_move

from anims.flicker import FlickerAnim
from anims.shake import ShakeAnim
from anims.jump import JumpAnim


class MageClone(DungeonActor):
  expires = True

  class ChargeAnim(ShakeAnim): pass

  def __init__(mage, *args, faction="enemy", **kwargs):
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

  def kill(mage, game):
    super().kill(game)
    anim_group = next((g for g in game.anims for a in g if a.target is mage), [])
    not anim_group in game.anims and game.anims.append(anim_group)
    anim_group.append(JumpAnim(
      target=mage,
      height=8,
    ))
    mage.inflict_ailment("freeze")
    mage.core.anims = [MageCore.TeaseAnim()]
    mage.shatter(game)

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
