from lib.sprite import Sprite
import assets

from dungeon.actors import DungeonActor
from cores import Core, Stats
from skills.weapon.tackle import Tackle

class DesertEvilCactus(DungeonActor):

  @staticmethod
  def get_idle_sprite(facing):
    if facing == (0, 1):
      return assets.sprites["cactus_down"]

    if facing == (0, -1):
      return assets.sprites["cactus_up"]

    return assets.sprites["cactus_side"]

  def __init__(cactus, name="Cackletus", *args, **kwargs):
    super().__init__(Core(
      name=name,
      faction="enemy",
      stats=Stats(
        hp=40,
        st=12,
        dx=4,
        ag=5,
        en=4,
      ),
      skills=[Tackle],
    ), *args, **kwargs)

  def view(cactus, anims):
    return super().view([Sprite(
      image=cactus.get_idle_sprite(cactus.facing)
    )], anims)
