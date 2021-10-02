from math import inf
from anims import Anim

class TweenAnim(Anim):
  blocking = True
  duration = 0

  def __init__(anim, easing=None, duration=inf, *args, **kwargs):
    super().__init__(duration=anim.duration or duration, *args, **kwargs)
    anim.easing = easing
    anim.pos = 0

  def update(anim):
    time = super().update()
    if anim.done:
      return 1
    anim.pos = max(0, time / anim.duration)
    if anim.easing:
      anim.pos = anim.easing(anim.pos)
    return anim.pos
