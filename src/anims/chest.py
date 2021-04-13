import math

FRAMES = 4

class ChestAnim:
  def __init__(anim, duration, target, item, on_end=None):
    anim.duration = duration
    anim.target = target
    anim.item = item
    anim.on_end = on_end
    anim.done = False
    anim.time = 0

  def update(anim):
    if anim.done:
      return -1
    anim.time += 1
    if anim.time == anim.duration:
      anim.done = True
      if anim.on_end:
        anim.on_end()
    return min(FRAMES - 1, math.floor(anim.time / anim.duration * 2 * FRAMES))
