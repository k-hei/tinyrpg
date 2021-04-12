class TweenAnim():
  def __init__(anim, duration, delay=0, target=None, on_end=None):
    anim.done = False
    anim.time = -delay
    anim.duration = duration
    anim.target = target
    anim.on_end = on_end

  def update(anim):
    if anim.done:
      return 1
    anim.time += 1
    if anim.time == anim.duration:
      anim.done = True
      if anim.on_end:
        anim.on_end()
    return max(0, anim.time / anim.duration)
