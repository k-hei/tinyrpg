from lib.sprite import Sprite
import assets

from dungeon.actors import DungeonActor
from cores import Core, Stats
from skills.weapon.tackle import Tackle

class DesertSnake(DungeonActor):
  def __init__(cactus, name="KingTuto", *args, **kwargs):
    super().__init__(Core(
      name=name,
      faction="enemy",
      stats=Stats(
        hp=25,
        st=12,
        dx=4,
        ag=5,
        en=4,
      ),
      skills=[Tackle],
    ), *args, **kwargs)

  def view(cactus, anims):
    return super().view([Sprite(
      image=assets.sprites["snake"]
    )], anims)
