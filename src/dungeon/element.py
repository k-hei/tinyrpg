from pygame import Surface
from sprite import Sprite
from anims.move import MoveAnim
from anims.chest import ChestAnim
from anims.item import ItemAnim
from anims.flicker import FlickerAnim
from lib.lerp import lerp
from config import ITEM_OFFSET, TILE_SIZE

class DungeonElement:
  def __init__(elem, solid=True, opaque=False):
    elem.solid = solid
    elem.opaque = opaque
    elem.cell = None

  def effect(elem, game):
    pass

  def aftereffect(elem, game):
    pass

  def view(elem, sprites, anims=[]):
    if type(sprites) is Surface:
      sprites = Sprite(image=sprites, layer="elems")
    if type(sprites) is Sprite:
      sprites = [sprites]
    sprite = sprites[0]
    sprite_width, sprite_height = sprite.size or sprite.image.get_size()
    offset_x, offset_y = (0, 0)
    item = None
    anim_group = anims[0] if anims else []
    for anim in [a for a in anim_group if a.target is elem]:
      if type(anim) is MoveAnim:
        anim_x, anim_y = anim.cell
        elem_x, elem_y = elem.cell
        offset_x = (anim_x - elem_x) * TILE_SIZE
        offset_y = (anim_y - elem_y) * TILE_SIZE
      elif type(anim) is ChestAnim or type(anim) is ItemAnim:
        t = anim.time / anim.duration
        item_image = anim.item.render()
        item_z = min(1, t * 3) * 6 + ITEM_OFFSET
        item_x, item_y = elem.cell
        item_x = (item_x + 0.5) * TILE_SIZE
        item_y = (item_y + 0.5) * TILE_SIZE - item_z
        sprites.append(Sprite(
          image=item_image,
          pos=(item_x, item_y),
          origin=("center", "center"),
          layer="numbers"
        ))
      elif type(anim) is FlickerAnim and anim.time % 2:
        return []
      elif type(anim) is FlickerAnim:
        pinch_duration = anim.duration // 2
        t = max(0, anim.time - anim.duration + pinch_duration) / pinch_duration
        sprite_width *= lerp(1, 0, t)
        sprite_height *= lerp(1, 3, t)

    # HACK: if element will move during a future animation sequence,
    # make sure it doesn't jump ahead to the target position
    for group in anims:
      for anim in group:
        if anims.index(group) == 0:
          continue
        if anim.target is elem and isinstance(anim, MoveAnim):
          anim_x, anim_y = anim.src
          actor_x, actor_y = elem.cell
          offset_x = (anim_x - actor_x) * TILE_SIZE
          offset_y = (anim_y - actor_y) * TILE_SIZE

    sprite.size = (sprite_width, sprite_height)
    sprite.move((offset_x, offset_y))
    return sprites
