from math import inf
from anims import Anim

class TweenAnim(Anim):
  blocking = True
  duration = 1

  def __init__(anim, easing=None, duration=0, *args, **kwargs):
    super().__init__(duration=duration or anim.duration, *args, **kwargs)
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
