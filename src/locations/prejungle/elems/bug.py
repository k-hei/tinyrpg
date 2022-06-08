from lib.sprite import Sprite
import assets
from dungeon.actors import DungeonActor
from cores import Core, Stats
from skills.weapon.tackle import Tackle

class PrejungleBug(DungeonActor):
  def __init__(bug, name="Mooper", *args, **kwargs):
    super().__init__(Core(
      name=name,
      faction="enemy",
      stats=Stats(
        hp=23,
        st=13,
        dx=4,
        ag=4,
        en=11,
      ),
      skills=[Tackle],
    ), *args, **kwargs)

  def view(bug, anims):
    return super().view([Sprite(
      image=assets.sprites["prejungle_bug"],
      pos=(0, 0)
    )], anims)
