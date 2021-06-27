from pygame import Rect
from dungeon.props import Prop
from assets import load as use_assets
from sprite import Sprite
from anims.move import MoveAnim
from anims import Anim
from filters import replace_color
from palette import BLACK, GREEN

class SinkAnim(Anim):
  GRAVITY_ACCEL = 0.0625
  GRAVITY_FACTOR = 1.0625
  DEPTH = 12
  BOUNCE = 0.75
  BOUNCES_MAX = 3

  def __init__(anim, *args, **kwargs):
    super().__init__(*args, **kwargs)
    anim.z = 0
    anim.vel = 0
    anim.bounces = 0

  def update(anim):
    super().update()
    if anim.vel <= 0 or anim.bounces:
      anim.vel += SinkAnim.GRAVITY_ACCEL
    else:
      anim.vel *= SinkAnim.GRAVITY_FACTOR
    anim.z += anim.vel
    if anim.z > SinkAnim.DEPTH:
      anim.z = SinkAnim.DEPTH
      if anim.bounces < SinkAnim.BOUNCES_MAX:
        anim.vel *= -SinkAnim.BOUNCE
        anim.bounces += 1
      else:
        anim.done = True
    return anim.z

class Block(Prop):
  def __init__(block):
    super().__init__()
    block.placed = False

  def effect(block, game):
    hero = game.hero
    block_x, block_y = block.cell
    delta_x, delta_y = hero.facing
    target_cell = (block_x + delta_x, block_y + delta_y)
    target_tile = game.floor.get_tile_at(target_cell)
    target_elem = game.floor.get_elem_at(target_cell)
    if block.placed or target_tile is None or target_tile.solid or target_elem:
      return None
    game.anims.append([
      MoveAnim(
        duration=45,
        target=hero,
        src=hero.cell,
        dest=block.cell
      ),
      MoveAnim(
        duration=45,
        target=block,
        src=block.cell,
        dest=target_cell
      )
    ])
    if target_tile is game.floor.PUSH_TILE:
      block.placed = True
      game.anims.append([
        SinkAnim(target=block)
      ])
    hero.cell = block.cell
    block.cell = target_cell
    return False

  def view(block, anims):
    block_image = use_assets().sprites["pushblock"]
    block_z = 0
    anim_group = [a for a in anims[0] if a.target is block] if anims else []
    for anim in anim_group:
      if type(anim) is SinkAnim:
        block_z = anim.z
    if not anim_group:
      if block.placed:
        block_z = SinkAnim.DEPTH
        block_image = replace_color(block_image, BLACK, GREEN)
    if block_z:
      block_image = block_image.subsurface(Rect(
        (0, 0),
        (block_image.get_width(), block_image.get_height() - block_z)
      ))
    return super().view(Sprite(
      image=block_image,
      pos=(0, 0),
      layer="elems" if anim_group or not block.placed else "decors"
    ), anims)
