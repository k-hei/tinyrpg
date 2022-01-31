from pygame import Surface, Rect, SRCALPHA
from pygame.transform import flip
import lib.vector as vector
from lib.sprite import Sprite
import assets
from dungeon.element import DungeonElement as Element

tree_surface = Surface((96, 96), SRCALPHA)
tree_surface.blit(assets.sprites["prejungle_berrytree_arm"], (0, 0))
tree_surface.blit(assets.sprites["prejungle_berrytree_head"], (32, 0))
tree_surface.blit(flip(assets.sprites["prejungle_berrytree_arm"], True, False), (64, 0))
tree_surface.blit(assets.sprites["prejungle_berrytree_tail"], (0, 32))
tree_surface.blit(assets.sprites["prejungle_berrytree_trunk"], (32, 32))
tree_surface.blit(assets.sprites["prejungle_berrytree_base"], (32, 64))
assets.sprites["prejungle_berrytree"] = tree_surface

class PrejungleBerryTree(Element):
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
      image=assets.sprites["prejungle_berrytree"],
      pos=(0, 16),
      origin=Sprite.ORIGIN_BOTTOM,
      layer="elems",
    )], *args, **kwargs)
