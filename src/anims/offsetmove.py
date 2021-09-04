from math import sqrt
from config import TILE_SIZE
from anims.tween import TweenAnim

class OffsetMoveAnim(TweenAnim):
  def __init__(anim, src, dest, speed=8, *args, **kwargs):
    super().__init__(*args, **kwargs)
    src_x, src_y = src
    dest_x, dest_y = dest
    dist_x, dist_y = (dest_x - src_x, dest_y - src_y)
    dist = sqrt(dist_x * dist_x + dist_y * dist_y)
    anim.offset = (0, 0)
    anim.normal = (dist_x / dist, dist_y / dist)
    anim.speed = speed / TILE_SIZE
    anim.duration = int(dist / anim.speed)

  def update(anim):
    super().update()
    x, y = anim.offset
    norm_x, norm_y = anim.normal
    anim.offset = (x + norm_x * anim.speed, y + norm_y * anim.speed)
    return anim.offset
