import math

class FrameAnim:
  def __init__(anim, duration, frame_count, delay=0, target=None, on_start=None, on_end=None):
    anim.duration = duration
    anim.frame_count = frame_count
    anim.delay = delay
    anim.target = target
    anim.on_start = on_start
    anim.on_end = on_end
    anim.done = False
    anim.time = -delay

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
      return -1
    t = anim.time / anim.duration
    delay = anim.duration // anim.frame_count
    frame = anim.time // delay
    frame = min(anim.frame_count - 1, frame)
    return frame
