from math import inf

class Anim:
  blocking = False

  def __init__(anim, duration=inf, delay=0, target=None, on_start=None, on_end=None):
    anim.duration = duration
    anim.time = -delay
    anim.target = target
    anim.on_start = on_start
    anim.on_end = on_end
    anim.done = False

  def update(anim):
    if anim.done:
      return -1
    if anim.time == 0:
      if anim.on_start:
        anim.on_start()
    anim.time += 1
    if anim.time == anim.duration:
      anim.done = True
      if anim.on_end:
        anim.on_end()
    if anim.time < 0:
      return 0
    return anim.time
