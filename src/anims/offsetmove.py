from math import sqrt
from config import TILE_SIZE
from anims.tween import TweenAnim
from lib.lerp import lerp

class OffsetMoveAnim(TweenAnim):
  def __init__(anim, src, dest, speed=8, *args, **kwargs):
    super().__init__(*args, **kwargs)
    src_x, src_y = src
    dest_x, dest_y = dest
    dist_x, dist_y = (dest_x - src_x, dest_y - src_y)
    dist = sqrt(dist_x * dist_x + dist_y * dist_y)
    anim.src = src
    anim.dest = dest
    anim.offset = (0, 0)
    anim.normal = (dist_x / dist, dist_y / dist)
    anim.speed = speed / TILE_SIZE
    anim.duration = int(dist / anim.speed)

  def update(anim):
    super().update()
    if anim.done:
      anim.offset = (0, 0)
      return anim.offset
    src_x, src_y = anim.src
    dest_x, dest_y = anim.dest
    anim.offset = (
      lerp(src_x, dest_x, anim.pos) - src_x,
      lerp(src_y, dest_y, anim.pos) - src_y
    )
    return anim.offset
