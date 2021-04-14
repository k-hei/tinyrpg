class FlickerAnim():
  def __init__(anim, duration, target, on_end=None):
    anim.done = False
    anim.time = 0
    anim.visible = False
    anim.duration = duration
    anim.target = target
    anim.on_end = on_end

  def update(anim):
    if anim.done:
      return False
    anim.time += 1
    if anim.time == anim.duration:
      anim.done = True
      if anim.on_end:
        anim.on_end()
    anim.visible = anim.time % 2 == 0
    return anim.visible
