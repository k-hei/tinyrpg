from anims import Anim
from lib.lerp import lerp

class MoveAnim(Anim):
  def __init__(anim, src, dest, *args, **kwargs):
    super().__init__(*args, **kwargs)
    anim.cell = src
    anim.src = src
    anim.dest = dest

  def update(anim):
    if super().update() == -1:
      return anim.dest
    src_x, src_y = anim.src
    dest_x, dest_y = anim.dest
    t = anim.time / anim.duration
    x = lerp(src_x, dest_x, t)
    y = lerp(src_y, dest_y, t)
    anim.cell = (x, y)
    return anim.cell
