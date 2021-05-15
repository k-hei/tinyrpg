from cores import Core
from sprite import Sprite
from assets import load as use_assets
from anims.walk import WalkAnim

class KnightCore(Core):
  def __init__(knight, skills=[]):
    super().__init__(
      name="Knight",
      faction="player",
      hp=23,
      st=15,
      en=9,
      skills=skills
    )

  def render(knight):
    sprites = use_assets().sprites
    image = None
    flip_x = False
    flip_y = False
    for anim in knight.anims:
      if type(anim) is WalkAnim:
        if knight.facing == (0, 1):
          if anim.frame_index % 2:
            image = sprites["knight_walkdown"]
          else:
            image = sprites["knight_down"]
          if anim.frame_index >= 2:
            flip_x = True
        else:
          if anim.frame_index % 2:
            image = sprites["knight_walk"]
          else:
            image = sprites["knight"]
        break
    else:
      if knight.facing == (0, 1):
        image = sprites["knight_down"]
      else:
        image = sprites["knight"]
    sprite = Sprite(image, flip=(flip_x, flip_y)) if image else None
    return super().render(sprite)
