from lib.lerp import lerp
from easing.expo import ease_in, ease_out

class BounceAnim:
  def __init__(anim, target, duration=45, on_squish=None, on_squash=None, on_end=None):
    anim.duration = duration
    anim.target = target
    anim.on_squish = on_squish
    anim.on_squash = on_squash
    anim.on_end = on_end
    anim.done = False
    anim.time = 0
    anim.scale = (1, 1)
    anim.phase = "squish"

  def update(anim):
    if anim.done:
      return -1
    anim.time += 1
    if anim.time == anim.duration:
      anim.done = True
      if anim.on_end:
        anim.on_end()
    scale_x, scale_y = anim.scale
    squish_duration = anim.duration // 4
    squash_duration = anim.duration // 2
    return_duration = anim.duration // 4
    if anim.phase == "squish":
      t = ease_in(anim.time / squish_duration)
      scale_x = lerp(1, 0.5, t)
      scale_y = lerp(1, 1.5, t)
      if anim.time == squish_duration:
        anim.on_squish and anim.on_squish()
        anim.phase = "squash"
    elif anim.phase == "squash":
      time = anim.time - squish_duration
      t = time / squash_duration
      scale_x = lerp(0.5, 2, t)
      scale_y = lerp(1.5, 0.5, t)
      if time == squash_duration:
        anim.on_squash and anim.on_squash()
        anim.phase = "return"
    elif anim.phase == "return":
      time = anim.time - squish_duration - squash_duration
      t = ease_out(time / return_duration)
      scale_x = lerp(2, 1, t)
      scale_y = lerp(0.5, 1, t)
    anim.scale = (scale_x, scale_y)
    return anim.scale
