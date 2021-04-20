class FlinchAnim():
  def __init__(anim, duration, target, on_start=None, on_end=None):
    anim.duration = duration
    anim.target = target
    anim.on_start = on_start
    anim.on_end = on_end
    anim.done = False
    anim.time = 0
    anim.x = 0

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
    anim.x = 0 if anim.time % 4 >= 2 else 1
    return anim.x
