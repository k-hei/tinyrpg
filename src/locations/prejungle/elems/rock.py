from pygame import Rect
import lib.vector as vector
from lib.sprite import Sprite
import assets
from dungeon.element import DungeonElement as Element

class PrejungleRockXL(Element):
  size = (2, 1)
  solid = True
  static = True

  @property
  def rect(rock):
    if rock._rect is None and rock.pos:
      rock._rect = Rect(
        vector.add(rock.pos, (-12, -32)),
        (52, 48)
      )
    return rock._rect

  def view(rock, *args, **kwargs):
    return super().view([Sprite(
      image=assets.sprites["prejungle_rock_xl"],
      pos=(-16, 16),
      origin=Sprite.ORIGIN_BOTTOMLEFT,
      layer="elems",
    )], *args, **kwargs)
