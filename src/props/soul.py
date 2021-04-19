from props import Prop
from assets import load as use_assets
from anims.frame import FrameAnim
from filters import replace_color
from comps.skill import Skill
import palette
import random

class Soul(Prop):
  ANIM_FRAMES = 5
  ANIM_PERIOD = 45
  ANIM_SWIVEL_PERIOD = 90
  ANIM_FLOAT_PERIOD = 45

  def __init__(soul, skill=None):
    super().__init__(solid=False)
    soul.skill = skill
    soul.time = random.randrange(0, Soul.ANIM_SWIVEL_PERIOD)

  def render(soul, anims):
    sprites = use_assets().sprites
    soul.time += 1
    if soul.time % 2:
      return None
    delay = Soul.ANIM_PERIOD // Soul.ANIM_FRAMES
    frame = soul.time % Soul.ANIM_PERIOD // delay
    frame = min(Soul.ANIM_FRAMES - 1, frame)
    sprite = sprites["soul" + str(frame)]
    if soul.skill:
      color = Skill.get_color(soul.skill)
      sprite = replace_color(sprite, palette.BLACK, color)
    return sprite
