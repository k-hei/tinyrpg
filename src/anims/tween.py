from math import inf
from anims import Anim

class TweenAnim(Anim):
  blocking = True

  def __init__(anim, easing=None, *args, **kwargs):
    super().__init__(*args, **kwargs)
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
