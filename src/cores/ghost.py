from math import pi, sin
from cores import Core
import assets
from sprite import Sprite
from filters import ripple
from anims.frame import FrameAnim

FLOAT_PERIOD = 180
FLOAT_AMP = 2

class Ghost(Core):
  class LaughAnim(FrameAnim):
    frames = assets.sprites["ghost_laugh"]
    frames_duration = 10
    loop = True

  def __init__(ghost, name="Ghost", faction="enemy", *args, **kwargs):
    super().__init__(name=name, faction=faction, *args, **kwargs)
    ghost.time = 0

  def update(ghost):
    super().update()
    ghost.time += 1

  def view(ghost, sprites=[]):
    ghost_anim = ghost.anims and ghost.anims[0]
    if ghost_anim and isinstance(ghost_anim, FrameAnim):
      ghost_image = ghost_anim.frame()
    else:
      ghost_image = assets.sprites["ghost"]
    ghost_image = ripple(ghost_image, start=16, end=32, time=ghost.time)
    ghost_y = sin(ghost.time % FLOAT_PERIOD / FLOAT_PERIOD * 2 * pi) * FLOAT_AMP
    return super().view([Sprite(
      image=ghost_image,
      pos=(0, ghost_y)
    )])
