from pygame import Rect
import lib.vector as vector
from lib.sprite import Sprite
import assets
from dungeon.element import DungeonElement as Element

class PrejungleRedTree(Element):
  solid = True
  static = True

  @property
  def rect(tree):
    if tree._rect is None and tree.pos:
      tree._rect = Rect(
        vector.subtract(tree.pos, (8, 0)),
        (16, 16)
      )
    return tree._rect

  def view(tree, *args, **kwargs):
    return super().view([Sprite(
      image=assets.sprites["prejungle_redtree"],
      pos=(-16, 16),
      origin=Sprite.ORIGIN_BOTTOMLEFT,
      layer="elems",
    )], *args, **kwargs)
