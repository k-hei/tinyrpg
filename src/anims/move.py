from anims import Anim
from lib.lerp import lerp
from config import WALK_DURATION

class MoveAnim(Anim):
  def __init__(anim, src, dest, duration=WALK_DURATION, started=True, *args, **kwargs):
    super().__init__(duration=duration, *args, **kwargs)
    anim.cell = src
    anim.src = src
    anim.dest = dest
    anim.period = duration
    anim.started = started
    anim.facing = (0, 0)

  def start(anim):
    anim.started = True

  def update(anim):
    if not anim.started:
      return anim.src
    if super().update() == -1:
      return anim.dest
    src_x, src_y = anim.src
    dest_x, dest_y = anim.dest
    t = anim.time / anim.duration
    dist_x = dest_x - src_x
    dist_y = dest_y - src_y
    anim.facing = (dist_x and dist_x / abs(dist_x), dist_y and dist_y / abs(dist_y))
    x = lerp(src_x, dest_x, t)
    y = lerp(src_y, dest_y, t)
    anim.cell = (x, y)
    return anim.cell
