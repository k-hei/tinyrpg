from lerp import lerp

class FlinchAnim:
  def __init__(anim, duration, target, direction=None, on_start=None, on_end=None):
    anim.duration = duration
    anim.target = target
    anim.direction = direction
    anim.on_start = on_start
    anim.on_end = on_end
    anim.done = False
    anim.time = 0
    anim.offset = (0, 0)

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
    offset_x, offset_y = anim.offset
    if anim.direction:
      delta_x, delta_y = anim.direction
      p = anim.duration // 2
      t = anim.time % p / p
      if anim.time >= anim.duration // 2:
        t = 1 - t
      offset_x = lerp(0, delta_x * 8, t)
      offset_y = lerp(0, delta_y * 8, t)
    else:
      offset_x = 0 if anim.time % 4 >= 2 else 1
    anim.offset = (offset_x, offset_y)
    return anim.offset
