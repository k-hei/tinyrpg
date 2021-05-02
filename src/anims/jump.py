from math import sin, pi
from lib.lerp import lerp
from anims.move import MoveAnim

class JumpAnim(MoveAnim):
  HEIGHT = 12

  def __init__(anim, *args, **kwargs):
    super().__init__(*args, **kwargs)
    anim.offset = 0

  def update(anim):
    super().update()
    t = anim.time / anim.duration
    anim.offset = sin(t * pi) *-JumpAnim.HEIGHT
