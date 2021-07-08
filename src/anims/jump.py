from math import sin, pi
from lib.lerp import lerp
from anims.move import MoveAnim
from config import JUMP_DURATION

class JumpAnim(MoveAnim):
  HEIGHT = 12

  def __init__(anim, duration=JUMP_DURATION, src=None, dest=None, *args, **kwargs):
    super().__init__(duration=duration, src=src, dest=dest, *args, **kwargs)
    anim.offset = 0

  def update(anim):
    super().update()
    t = anim.time / anim.duration
    anim.offset = sin(t * pi) * -JumpAnim.HEIGHT
