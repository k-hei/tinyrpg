from lib.sprite import Sprite
import assets

from dungeon.actors import DungeonActor
from cores import Core, Stats
from skills.weapon.tackle import Tackle

class DesertEvilCactus(DungeonActor):
  def __init__(cactus, name="Cackletus", *args, **kwargs):
    super().__init__(Core(
      name=name,
      faction="enemy",
      stats=Stats(
        hp=21,
        st=9,
        dx=4,
        ag=10,
        en=7,
      ),
      skills=[Tackle],
    ), *args, **kwargs)

  def view(cactus, anims):
    return super().view([Sprite(
      image=assets.sprites["cactus"]
    )], anims)
