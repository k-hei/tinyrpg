from pygame import Surface, SRCALPHA
from pygame.transform import flip
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
  def view(tree, *args, **kwargs):
    return super().view([Sprite(
      image=assets.sprites["prejungle_berrytree"],
      pos=(0, 16),
      origin=Sprite.ORIGIN_BOTTOM,
      layer="elems",
    )], *args, **kwargs)
