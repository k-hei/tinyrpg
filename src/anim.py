class Anim:
  def __init__(anim, duration, data):
    anim.done = False
    anim.time = 0
    anim.duration = duration
    anim.data = data
  def update(anim):
    if anim.done:
      return -1
    anim.time += 1
    if anim.time == anim.duration:
      anim.done = True
    return anim.time / anim.duration
