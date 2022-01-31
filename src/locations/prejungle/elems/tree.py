from pygame import Surface, Rect, SRCALPHA
from pygame.transform import flip
import lib.vector as vector
from lib.sprite import Sprite
import assets
from dungeon.element import DungeonElement as Element

tree_surface = Surface((128, 160), SRCALPHA)
tree_surface.blit(assets.sprites["prejungle_tree_head"], (0, 0))
tree_surface.blit(flip(assets.sprites["prejungle_tree_head"], True, False), (64, 0))
tree_surface.blit(assets.sprites["prejungle_tree_trunk"], (32, 64))
tree_surface.blit(assets.sprites["prejungle_tree_trunk"], (32, 96))
tree_surface.blit(assets.sprites["prejungle_tree_base"], (32, 128))
assets.sprites["prejungle_tree"] = tree_surface

class PrejungleTree(Element):
  solid = True
  static = True

  @property
  def rect(tree):
    if tree._rect is None and tree.pos:
      tree._rect = Rect(
        vector.add(tree.pos, (-16, -16)),
        (32, 32)
      )
    return tree._rect

  def view(tree, *args, **kwargs):
    return super().view([Sprite(
      image=assets.sprites["prejungle_tree"],
      pos=(0, 16),
      origin=Sprite.ORIGIN_BOTTOM,
      layer="elems",
    )], *args, **kwargs)
