from math import inf

class Anim:
  blocking = False
  duration = 0
  loop = False

  def __init__(anim, duration=inf, delay=0, loop=False, target=None, on_start=None, on_end=None):
    anim.duration = anim.duration or duration
    anim.time = -delay
    if loop: anim.loop = loop
    anim.target = target
    anim.on_start = on_start
    anim.on_end = on_end
    anim.done = False

  def end(anim):
    anim.done = True
    if anim.on_end:
      anim.on_end()

  def update(anim):
    if anim.done:
      return -1
    if anim.time == 0:
      if anim.on_start:
        anim.on_start()
    anim.time += 1
    if anim.duration and anim.time == anim.duration and not anim.loop:
      anim.end()
    if anim.time < 0:
      return 0
    return anim.time
