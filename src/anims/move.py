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
    if anim.cell is None:
      return None
    src_x, src_y, src_z = anim.src
    dest_x, dest_y, dest_z = anim.dest
    dist_x = dest_x - src_x
    dist_y = dest_y - src_y
    anim.facing = (dist_x and dist_x / abs(dist_x), dist_y and dist_y / abs(dist_y))
    t = anim.time / anim.duration
    x = lerp(src_x, dest_x, t)
    y = lerp(src_y, dest_y, t)
    z = lerp(src_z, dest_z, t)
    anim.cell = (x, y, z)
    return anim.cell
