from math import floor, inf
from anims import Anim

class ShakeAnim(Anim):
  def __init__(anim, magnitude=1, duration=inf, *args, **kwargs):
    super().__init__(duration=duration, *args, **kwargs)
    anim.magnitude = magnitude
    anim.offset = 0

  def update(anim):
    time = super().update()
    if anim.done:
      return 0
    anim.offset = time // 2 % 2 and floor(-anim.magnitude) or floor(anim.magnitude)
    return anim.offset
