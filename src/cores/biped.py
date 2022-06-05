from dataclasses import dataclass
from cores import Core
from lib.sprite import Sprite
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
  WalkAnim = WalkAnim

  def view(actor):
    sprites = use_assets().sprites
    sprite_id = None
    flip_x = False
    flip_y = False
    facing_x, facing_y = actor.facing
    for anim in actor.anims:
      if isinstance(anim, WalkAnim):
        if facing_x < 0:
          walk_cycle = actor.sprites.walk_right
          flip_x = True
        elif facing_x > 0:
          walk_cycle = actor.sprites.walk_right
        elif facing_y < 0:
          walk_cycle = actor.sprites.walk_up
        elif facing_y > 0:
          walk_cycle = actor.sprites.walk_down
        sprite_id = walk_cycle[anim.frame_index]
        break
    else:
      facing_x, facing_y = actor.facing
      if facing_x == 1:
        sprite_id = actor.sprites.face_right
      elif facing_x == -1:
        sprite_id = actor.sprites.face_right
        flip_x = True
      elif facing_y == 1:
        sprite_id = actor.sprites.face_down or actor.sprites.face_right
      elif facing_y == -1:
        sprite_id = actor.sprites.face_up or actor.sprites.face_right
    image = sprites[sprite_id] if sprite_id else None
    sprite = Sprite(
      image=image,
      flip=(flip_x, flip_y),
      layer="elems"
    ) if image else None
    sprites = [sprite] if sprite else []
    return super().view(sprites)
