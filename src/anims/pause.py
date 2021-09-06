class PauseAnim():
  blocking = False

  def __init__(anim, duration, on_start=None, on_end=None):
    anim.target = None
    anim.done = False
    anim.time = 0
    anim.duration = duration
    anim.on_start = on_start
    anim.on_end = on_end

  def update(anim):
    if anim.done:
      return None
    if anim.time == 0:
      anim.on_start and anim.on_start()
    anim.time += 1
    if anim.time == anim.duration:
      anim.done = True
      anim.on_end and anim.on_end()
    return None
