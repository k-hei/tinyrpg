from dataclasses import dataclass
from cores import Core
from sprite import Sprite
from assets import load as use_assets
from anims.walk import WalkAnim

@dataclass
class SpriteMap:
  face_right: str = None
  face_down: str = None
  face_up: str = None
  walk_right: tuple = None
  walk_down: tuple = None
  walk_up: tuple = None

class BipedCore(Core):
  sprites = SpriteMap()

  def render(actor):
    sprites = use_assets().sprites
    sprite_id = None
    flip_x = False
    flip_y = False
    for anim in actor.anims:
      if type(anim) is WalkAnim:
        if actor.facing == (0, 1):
          walk_cycle = actor.sprites.walk_down
        elif actor.facing == (0, -1):
          walk_cycle = actor.sprites.walk_up
        elif actor.facing == (1, 0):
          walk_cycle = actor.sprites.walk_right
        elif actor.facing == (-1, 0):
          walk_cycle = actor.sprites.walk_right
          flip_x = True
        sprite_idx = int(anim.time % anim.period / anim.period * 4)
        sprite_id = walk_cycle[sprite_idx]
        break
    else:
      if actor.facing == (0, 1):
        sprite_id = actor.sprites.face_down or actor.sprites.face_right
      elif actor.facing == (0, -1):
        sprite_id = actor.sprites.face_down or actor.sprites.face_right
      else:
        sprite_id = actor.sprites.face_right
    image = sprites[sprite_id] if sprite_id else None
    sprite = Sprite(image, flip=(flip_x, flip_y)) if image else None
    return super().render(sprite)
