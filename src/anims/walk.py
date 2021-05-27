from math import inf
from config import MOVE_DURATION
from anims import Anim

class WalkAnim(Anim):
  def __init__(anim, period=MOVE_DURATION):
    super().__init__(duration=inf)
    anim.period = period
    anim.frame_index = -1

  def update(anim):
    if anim.done:
      return -1
    time = super().update()
    anim.frame_index = int(time % anim.period / anim.period * 4)
    return anim.frame_index
