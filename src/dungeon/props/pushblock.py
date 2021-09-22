from pygame import Rect
from dungeon.props import Prop
from dungeon.props.pushtile import PushTile
from assets import load as use_assets
from sprite import Sprite
from anims.move import MoveAnim
from anims import Anim
from filters import replace_color
from colors.palette import BLACK, WHITE, PURPLE, SAFFRON, DARKBLUE

class PushBlock(Prop):
  def __init__(block, placed=False):
    super().__init__(static=placed)

  def encode(block):
    [cell, kind, *props] = super().encode()
    props = {
      **(props[0] if props else {}),
      **(block.static and { "placed": True } or {}),
    }
    return [cell, kind, *(props and [props] or [])]

  def on_push(block, game):
    target_elem = game.floor.get_elem_at(block.cell, exclude=[PushBlock])
    if type(target_elem) is PushTile:
      block.static = True
      game.anims.append([
        SinkAnim(target=block)
      ])
      if target_elem:
        target_elem.effect(game)
    return True

  def view(block, anims):
    assets = use_assets()
    block_image = assets.sprites["push_block"]
    block_z = 0
    anim_group = [a for a in anims[0] if a.target is block] if anims else []
    for anim in anim_group:
      if type(anim) is SinkAnim:
        block_z = anim.z
    if not anim_group and block.static:
      block_z = SinkAnim.DEPTH
      block_image = assets.sprites["push_block_open"]
      block_image = replace_color(block_image, WHITE, PURPLE)
      block_image = replace_color(block_image, BLACK, DARKBLUE)
    else:
      block_image = replace_color(block_image, WHITE, SAFFRON)
    if block_z:
      block_image = block_image.subsurface(Rect(
        (0, 0),
        (block_image.get_width(), block_image.get_height() - block_z)
      ))
    return super().view([Sprite(
      image=block_image,
      pos=(0, 0),
      layer="elems"
    )], anims)

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
