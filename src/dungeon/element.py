from math import sin, pi
from pygame import Surface
from lib.sprite import Sprite
from anims import Anim
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
from config import ITEM_OFFSET, TILE_SIZE, PUSH_DURATION, NUDGE_DURATION
import debug

class DungeonElement:
  solid = False
  opaque = False
  static = False
  active = False
  hidden = False

  def __init__(elem, size=(1, 1), solid=False, opaque=False, static=False, active=False, hidden=False):
    if not elem.solid: elem.solid = solid
    if not elem.opaque: elem.opaque = opaque
    if not elem.static: elem.static = static
    if not elem.active: elem.active = active
    if not elem.hidden: elem.hidden = hidden
    if type(size) is not tuple:
      debug.log(f"WARNING: Create element {type(elem).__name__} with size {size}")
      size = (1, 1)
    elem.size = size
    elem.pos = None
    elem.elev = 0

  @property
  def cell(elem):
    if elem.pos is None:
      return None
    x, y = elem.pos
    return (x // elem.scale, y // elem.scale)

  @cell.setter
  def cell(elem, cell):
    col, row = cell
    elem.pos = (
      (col + 0.5) * elem.scale,
      (row + 1) * elem.scale
    )

  def encode(elem):
    return [(elem.cell), type(elem).__name__]

  def effect(elem, game):
    pass

  def on_nudge(elem, game): pass
  def on_push(elem, game): pass
  def on_enter(elem, game): pass
  def on_leave(elem, game): pass

  def spawn(elem, stage, cell):
    elem.scale = stage.tile_size
    elem.cell = cell
    tile = stage.get_tile_at(cell)
    if tile:
      elem.elev = tile.elev

  def step(elem, game):
    pass

  def update(elem, game):
    pass

  def find_move_offset(elem, anims):
    if isinstance(anims, Anim):
      return elem.find_move_anim_offset(anim=anims)
    for group in anims:
      for anim in group:
        if anim.target is not elem or not (isinstance(anim, MoveAnim) or type(anim) is PathAnim) or not anim.cell:
          continue
        if anims.index(group) == 0:
          return elem.find_move_anim_offset(anim)
        else:
          anim_x, anim_y, *anim_z = anim.src
          anim_z = anim_z and anim_z[0] or 0
          elem_x, elem_y = elem.cell
          return (
            (anim_x - elem_x) * TILE_SIZE,
            (anim_y - anim_z - elem_y) * TILE_SIZE
          )
    return (0, 0)

  def find_move_anim_offset(elem, anim):
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
    if sprites:
      sprite = sprites[0]
      sprite_width, sprite_height = sprite.size or sprite.image.get_size()
      sprite_layer = sprite.layer or "elems"
    else:
      sprite = None
      sprite_width, sprite_height = (0, 0)
      sprite_layer = "elems"
    offset_x, offset_y = elem.find_move_offset(anims)
    item = None
    moving = next((g for g in anims if next((a for a in g if a.target is elem and type(a) is MoveAnim), None)), None)
    anim_group = [a for a in anims[0] if a.target is elem] if anims else []
    for anim in anim_group:
      if (isinstance(anim, MoveAnim) or type(anim) is PathAnim) and anim.cell:
        if ((type(anim) is MoveAnim or type(anim) is PathAnim)
        and anim.facing != (0, 0)
        and not anim.duration in (PUSH_DURATION, NUDGE_DURATION)
        and not next((a for g in anims for a in g if a.target is elem and type(a) is FlinchAnim), None)):
          elem.facing = tuple(map(int, anim.facing))
      elif type(anim) is ItemAnim:
        item_image = anim.item.render()
        item_offset = min(12, 6 + anim.time // 2) + ITEM_OFFSET
        if anim.time > 30:
          item_offset += sin((anim.time - 30) % 90 / 90 * 2 * pi) * 2
        item_x, item_y = elem.cell
        item_x = 0
        item_y = -item_offset
        item_z = elem.elev * TILE_SIZE
        sprites.append(Sprite(
          image=item_image,
          pos=(item_x, item_y - item_z),
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
      elif isinstance(anim, ShakeAnim):
        offset_x += anim.offset
      elif type(anim) is FallAnim:
        offset_y = anim.y
        sprite_layer = "tiles"
      if type(anim) is JumpAnim:
        offset_y += anim.offset

    if sprite:
      sprite.size = (sprite_width, sprite_height)
      sprite.layer = sprite_layer
      sprite.move((offset_x, offset_y))
    return sprites
