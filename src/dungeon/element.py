from pygame import Surface
from sprite import Sprite
from anims.move import MoveAnim
from anims.chest import ChestAnim
from anims.item import ItemAnim
from anims.flicker import FlickerAnim
from anims.warpin import WarpInAnim
from anims.drop import DropAnim
from anims.shake import ShakeAnim
from anims.flinch import FlinchAnim
from anims.path import PathAnim
from lib.lerp import lerp
from config import ITEM_OFFSET, TILE_SIZE

class DungeonElement:
  def __init__(elem, solid=True, opaque=False):
    elem.solid = solid
    elem.opaque = opaque
    elem.cell = None
    elem.size = (1, 1)
    elem.elev = 0

  def encode(elem):
    return [(elem.cell), type(elem).__name__]

  def effect(elem, game):
    pass

  def aftereffect(elem, game):
    pass

  def spawn(elem, stage, cell):
    elem.cell = cell
    elem.elev = stage.get_tile_at(cell).elev

  def update(elem):
    pass

  def view(elem, sprites, anims=[]):
    will_enter = anims and next((g for g in anims if g is not anims[0] and next((a for a in g if (
      a.target is elem
      and (type(a) is WarpInAnim or type(a) is DropAnim)
    )), None)), None)
    if will_enter:
      return []
    if type(sprites) is Surface:
      sprites = Sprite(image=sprites, layer="elems")
    if type(sprites) is Sprite:
      sprites = [sprites]
    sprite = sprites[0]
    sprite_width, sprite_height = sprite.size or sprite.image.get_size()
    sprite_layer = sprite.layer or "elems"
    offset_x, offset_y = (0, 0)
    item = None
    moving = next((g for g in anims if next((a for a in g if a.target is elem and type(a) is MoveAnim), None)), None)
    anim_group = anims[0] if anims else []
    for anim in [a for a in anim_group if a.target is elem]:
      if type(anim) is MoveAnim or type(anim) is PathAnim:
        if offset_x or offset_y:
          continue
        anim_x, anim_y = anim.cell
        elem_x, elem_y = elem.cell
        offset_x = (anim_x - elem_x) * TILE_SIZE
        offset_y = (anim_y - elem_y) * TILE_SIZE
        if anim.facing != (0, 0) and not next((a for g in anims for a in g if a.target is elem and type(a) is FlinchAnim), None):
          elem.facing = anim.facing
      elif type(anim) is ChestAnim or type(anim) is ItemAnim:
        t = anim.time / anim.duration
        item_image = anim.item.render()
        item_z = min(1, t * 3) * 6 + ITEM_OFFSET
        item_x, item_y = elem.cell
        item_x = 0
        item_y = -item_z
        sprites.append(Sprite(
          image=item_image,
          pos=(item_x, item_y),
          origin=("center", "center"),
          layer="numbers"
        ))
      elif type(anim) is FlickerAnim and not anim.visible:
        return []
      elif type(anim) is FlickerAnim:
        pinch_duration = anim.duration // 2
        t = max(0, anim.time - anim.duration + pinch_duration) / pinch_duration
        sprite_width *= lerp(1, 0, t)
        sprite_height *= lerp(1, 3, t)
      elif type(anim) is WarpInAnim:
        scale_x, scale_y = anim.scale
        sprite_width *= scale_x
        sprite_height *= scale_y
      elif type(anim) is DropAnim:
        offset_y = -anim.y
      elif type(anim) is ShakeAnim:
        offset_x = anim.offset

    # HACK: if element will move during a future animation sequence,
    # make sure it doesn't jump ahead to the target position
    for group in anims:
      for anim in group:
        if anims.index(group) == 0:
          continue
        if anim.target is elem and isinstance(anim, MoveAnim) and anim.cell:
          anim_x, anim_y = anim.src
          actor_x, actor_y = elem.cell
          offset_x = (anim_x - actor_x) * TILE_SIZE
          offset_y = (anim_y - actor_y) * TILE_SIZE

    # if not moving:
    #   offset_y -= elem.elev * TILE_SIZE
    sprite.size = (sprite_width, sprite_height)
    sprite.layer = sprite_layer
    sprite.move((offset_x, offset_y))
    return sprites
