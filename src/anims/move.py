from lib.lerp import lerp

class MoveAnim():
  def __init__(anim, duration,  target, src_cell, dest_cell, started=True, on_end=None):
    anim.done = False
    anim.time = 0
    anim.duration = duration
    anim.target = target
    anim.cur_cell = src_cell
    anim.src_cell = src_cell
    anim.dest_cell = dest_cell
    anim.started = started
    anim.on_end = on_end

  def start(anim):
    anim.started = True

  def update(anim):
    if anim.done:
      return anim.dest_cell
    if not anim.started:
      return anim.src_cell
    anim.time += 1
    if anim.time == anim.duration:
      anim.done = True
      if anim.on_end:
        anim.on_end()
    src_x, src_y = anim.src_cell
    dest_x, dest_y = anim.dest_cell
    t = anim.time / anim.duration
    x = lerp(src_x, dest_x, t)
    y = lerp(src_y, dest_y, t)
    anim.cur_cell = (x, y)
    return anim.cur_cell
