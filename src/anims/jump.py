from math import sin, pi
from lib.lerp import lerp
from anims.step import StepAnim
from config import JUMP_DURATION

JUMP_HEIGHT = 12

class JumpAnim(StepAnim):
  def __init__(anim, height=JUMP_HEIGHT, duration=JUMP_DURATION, src=None, dest=None, *args, **kwargs):
    super().__init__(duration=duration, src=src, dest=dest, *args, **kwargs)
    anim.height = height
    anim.offset = 0

  def update(anim):
    super().update()
    t = min(1, max(0, anim.time) / anim.duration)
    anim.offset = sin(t * pi) * -anim.height
