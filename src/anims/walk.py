from math import inf
from config import MOVE_DURATION
from anims import Anim

class WalkAnim(Anim):
  def __init__(anim, period=MOVE_DURATION, vertical=False):
    super().__init__(duration=inf)
    anim.period = period
    anim.vertical = vertical
    anim.frame_index = -1

  def update(anim):
    if anim.done:
      return -1
    time = super().update()
    frame_index = 0
    if time % (anim.period // 2) >= anim.period // 4:
      frame_index += 1
    if anim.vertical and time % anim.period >= anim.period // 2:
      frame_index += 2
    anim.frame_index = frame_index
    return frame_index
