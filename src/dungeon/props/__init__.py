from dungeon.element import DungeonElement
from config import TILE_SIZE

class Prop(DungeonElement):
  def effect(prop, game, actor=None):
    pass

  def view(prop, sprites, anims):
    if not sprites:
      return []
    sprite = sprites[0]
    prop_xoffset, prop_yoffset = (0, 0)
    prop_yoffset -= prop.elev * TILE_SIZE
    sprite.move((prop_xoffset, prop_yoffset))
    return super().view([sprite, *sprites[1:]], anims)
