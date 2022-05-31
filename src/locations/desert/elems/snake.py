from lib.sprite import Sprite
import assets

from dungeon.actors import DungeonActor
from cores import Core, Stats
from skills.weapon.tackle import Tackle

class DesertSnake(DungeonActor):

  @staticmethod
  def get_idle_sprite(facing):
    if facing == (0, 1):
      return assets.sprites["snake_down"]

    if facing == (0, -1):
      return assets.sprites["snake_up"]

    return assets.sprites["snake_side"]

  def __init__(snake, name="KingTuto", *args, **kwargs):
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

  def view(snake, anims):
    return super().view([Sprite(
      image=snake.get_idle_sprite(snake.facing)
    )], anims)
