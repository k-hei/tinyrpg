from lib.sprite import Sprite
import assets

from dungeon.actors import DungeonActor
from cores import Core


class Roko(DungeonActor):
  def __init__(roko, message, *args, **kwargs):
    super().__init__(Core(
      name="Roko",
      faction="ally",
      message=message,
    ), *args, **kwargs)

  def view(roko, anims):
    return super().view([Sprite(
      image=assets.sprites["roko"],
    )], anims)
