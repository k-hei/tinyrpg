from math import sqrt
from anims import Anim
from config import ATTACK_DURATION, TILE_SIZE

class AttackAnim(Anim):
  def __init__(anim, src, dest, duration=ATTACK_DURATION, amplitude=16, on_connect=None, *args, **kwargs):
    super().__init__(duration=duration, *args, **kwargs)
    src_x, src_y = src
    dest_x, dest_y = dest
    disp_x, disp_y = (dest_x - src_x, dest_y - src_y)
    dist = sqrt(disp_x * disp_x + disp_y * disp_y) or 1
    normal = (disp_x / dist, disp_y / dist)
    anim.cell = src
    anim.src = src
    anim.dest = dest
    anim.amplitude = amplitude
    anim.normal = normal
    anim.on_connect = on_connect

  def update(anim):
    time = super().update()
    if anim.done:
      return anim.dest
    src_x, src_y = anim.src
    norm_x, norm_y = anim.normal
    midpoint = anim.duration // 2
    if time == midpoint:
      anim.on_connect and anim.on_connect()
    steps = time if time <= midpoint else midpoint * 2 - time
    t = steps / midpoint
    x = src_x + norm_x * t * anim.amplitude / TILE_SIZE
    y = src_y + norm_y * t * anim.amplitude / TILE_SIZE
    anim.cell = (x, y)
    return anim.cell
