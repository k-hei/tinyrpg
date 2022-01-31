from pygame import Rect
import lib.vector as vector
from lib.sprite import Sprite
import assets
from dungeon.element import DungeonElement as Element

class PrejungleBush(Element):
  def view(rock, *args, **kwargs):
    return super().view([Sprite(
      image=assets.sprites["prejungle_bush"],
      pos=(-16, 16),
      origin=Sprite.ORIGIN_BOTTOMLEFT,
      layer="elems",
    )], *args, **kwargs)
