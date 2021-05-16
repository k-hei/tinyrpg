from dataclasses import dataclass
from cores import Core
from sprite import Sprite
from assets import load as use_assets
from anims.walk import WalkAnim

@dataclass
class SpriteMap:
  face_right: str = None
  walk_right: str = None
  face_down: str = None
  walk_down: str = None

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
          if anim.frame_index % 2:
            sprite_id = actor.sprites.walk_down
          else:
            sprite_id = actor.sprites.face_down
          if anim.frame_index >= 2:
            flip_x = True
        else:
          if anim.frame_index % 2:
            sprite_id = actor.sprites.walk_right
          else:
            sprite_id = actor.sprites.face_right
        break
    else:
      if actor.facing == (0, 1):
        sprite_id = actor.sprites.face_down
      else:
        sprite_id = actor.sprites.face_right
    image = sprites[sprite_id] if sprite_id else None
    sprite = Sprite(image, flip=(flip_x, flip_y)) if image else None
    return super().render(sprite)
