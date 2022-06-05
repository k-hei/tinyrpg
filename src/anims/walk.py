from math import inf
from config import MOVE_DURATION
from anims import Anim

class WalkAnim(Anim):
  period = MOVE_DURATION
  frame_count = 4

  def __init__(anim, period=0, frame_count=0):
    super().__init__(duration=inf)
    anim.frame_index = -1
    if period: anim.period = period
    if frame_count: anim.frame_count = frame_count

  def update(anim):
    if anim.done:
      return -1
    time = super().update()
    anim.frame_index = int(time % anim.period / anim.period * anim.frame_count)
    return anim.frame_index
