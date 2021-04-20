import math

class AttackAnim:
  def __init__(anim, duration, target, src_cell, dest_cell, on_connect=None, on_end=None):
    src_x, src_y = src_cell
    dest_x, dest_y = dest_cell
    disp_x, disp_y = (dest_x - src_x, dest_y - src_y)
    dist = math.sqrt(disp_x * disp_x + disp_y * disp_y)
    normal = (disp_x / dist, disp_y / dist)
    anim.done = False
    anim.time = 0
    anim.duration = duration
    anim.target = target
    anim.cur_cell = src_cell
    anim.src_cell = src_cell
    anim.dest_cell = dest_cell
    anim.normal = normal
    anim.on_connect = on_connect
    anim.on_end = on_end

  def update(anim):
    if anim.done:
      return anim.dest
    anim.time += 1
    if anim.time == anim.duration:
      anim.done = True
      if anim.on_end:
        anim.on_end()
    src_x, src_y = anim.src_cell
    norm_x, norm_y = anim.normal
    midpoint = anim.duration // 2
    if anim.time == midpoint:
      if anim.on_connect:
        anim.on_connect()
    steps = anim.time if anim.time <= midpoint else midpoint - anim.time + midpoint
    x = src_x + norm_x / 16 * steps
    y = src_y + norm_y / 16 * steps
    anim.cur_cell = (x, y)
    return anim.cur_cell
