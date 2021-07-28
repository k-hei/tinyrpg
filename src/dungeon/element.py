from math import sin, pi
from pygame import Surface
from sprite import Sprite
from anims.move import MoveAnim
from anims.item import ItemAnim
from anims.flicker import FlickerAnim
from anims.warpin import WarpInAnim
from anims.jump import JumpAnim
from anims.drop import DropAnim
from anims.shake import ShakeAnim
from anims.flinch import FlinchAnim
from anims.fall import FallAnim
from anims.path import PathAnim
from lib.lerp import lerp
import lib.vector as vector
from config import ITEM_OFFSET, TILE_SIZE, PUSH_DURATION

class DungeonElement:
  static = False

  def __init__(elem, solid=True, opaque=False, static=False):
    elem.solid = solid
    elem.opaque = opaque
    if not elem.static:
      elem.static = static
    elem.cell = None
    elem.size = (1, 1)
    elem.elev = 0

  def encode(elem):
    return [(elem.cell), type(elem).__name__]

  def effect(elem, game):
    pass

  def aftereffect(elem, game):
    pass

  def on_nudge(elem, game): pass
  def on_push(elem, game): pass
  def on_enter(elem, game): pass
  def on_leave(elem, game): pass

  def spawn(elem, stage, cell):
    elem.cell = cell
    elem.elev = stage.get_tile_at(cell).elev

  def update(elem):
    pass

  def get_move_offset(elem, anim):
    anim_x, anim_y, *anim_z = anim.cell
    anim_z = max(0, anim_z and anim_z[0] or 0)
    elem_x, elem_y = elem.cell
    offset_x = (anim_x - elem_x) * TILE_SIZE
    offset_y = (anim_y - anim_z - elem_y) * TILE_SIZE
    return (offset_x, offset_y)

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
        # if offset_x or offset_y:
        #   continue
        offset_x, offset_y = vector.add((offset_x, offset_y), elem.get_move_offset(anim))
        if (anim.facing != (0, 0)
        and not anim.duration == PUSH_DURATION
        and not next((a for g in anims for a in g if a.target is elem and type(a) is FlinchAnim), None)):
          elem.facing = tuple(map(int, anim.facing))
      elif type(anim) is ItemAnim:
        item_image = anim.item.render()
        item_z = min(12, 6 + anim.time // 2) + ITEM_OFFSET
        if anim.time > 30:
          item_z += sin((anim.time - 30) % 90 / 90 * 2 * pi) * 2
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
      if type(anim) is JumpAnim:
        offset_y += anim.offset
      elif type(anim) is DropAnim:
        offset_y = -anim.y
      elif type(anim) is ShakeAnim:
        offset_x += anim.offset
      elif type(anim) is FallAnim:
        offset_y = anim.y
        sprite_layer = "tiles"

    # HACK: if element will move during a future animation sequence,
    # make sure it doesn't jump ahead to the target position
    for group in anims:
      for anim in group:
        if anims.index(group) == 0:
          continue
        if anim.target is elem and isinstance(anim, MoveAnim) and anim.cell:
          anim_x, anim_y, *anim_z = anim.src
          anim_z = anim_z and anim_z[0] or 0
          actor_x, actor_y = elem.cell
          offset_x = (anim_x - actor_x) * TILE_SIZE
          offset_y = (anim_y - anim_z - actor_y) * TILE_SIZE

    # if not moving:
    #   offset_y -= elem.elev * TILE_SIZE
    sprite.size = (sprite_width, sprite_height)
    sprite.layer = sprite_layer
    sprite.move((offset_x, offset_y))
    return sprites
