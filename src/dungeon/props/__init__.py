from dungeon.element import DungeonElement
from config import TILE_SIZE
from anims.move import MoveAnim

class Prop(DungeonElement):
  def effect(prop, game, actor=None):
    pass

  def view(prop, sprites, anims):
    if not sprites:
      return super().view([], anims)
    sprite = sprites[0]
    prop_xoffset, prop_yoffset = (0, 0)
    move_anim = anims and next((a for a in anims[0] if a.target is prop and isinstance(a, MoveAnim)), None)
    if not move_anim or not move_anim.cell:
      prop_yoffset -= prop.elev * TILE_SIZE
    sprite.move((prop_xoffset, prop_yoffset))
    return super().view([sprite, *sprites[1:]], anims)
