from anims import Anim
from lib.lerp import lerp

class FlinchAnim(Anim):
  def __init__(anim, direction=None,  *args, **kwargs):
    super().__init__(*args, **kwargs)
    anim.direction = direction
    anim.offset = (0, 0)

  def update(anim):
    super().update()
    if anim.done:
      anim.offset = (0, 0)
      return anim.offset
    offset_x, offset_y = anim.offset
    if anim.direction:
      delta_x, delta_y = anim.direction
      p = anim.duration // 2
      if anim.time < p:
        t = anim.time / p
      else:
        t = 1 - (anim.time - p) / p
      offset_x = lerp(0, delta_x * 8, t)
      offset_y = lerp(0, delta_y * 8, t)
    else:
      offset_x = 0 if anim.time % 4 >= 2 else 1
    anim.offset = (offset_x, offset_y)
    return anim.offset
