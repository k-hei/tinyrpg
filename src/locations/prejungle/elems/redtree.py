from lib.sprite import Sprite
import assets
from dungeon.element import DungeonElement as Element

class PrejungleRedTree(Element):
  def view(tree, *args, **kwargs):
    return super().view([Sprite(
      image=assets.sprites["prejungle_redtree"],
      pos=(-16, 16),
      origin=Sprite.ORIGIN_BOTTOMLEFT,
      layer="elems",
    )], *args, **kwargs)
