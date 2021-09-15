from anims import Anim
from config import WALK_DURATION
from lib.lerp import lerp

class PathAnim(Anim):
  def __init__(anim, path, period=WALK_DURATION, duration=None, on_step=None, *args, **kwargs):
    super().__init__(duration=duration, *args, **kwargs)
    anim.period = period
    anim.path = path
    anim.src = path[0]
    anim.cell = anim.src
    anim.next_cell = path[1] if len(path) > 1 else None
    anim.facing = (0, 0)
    anim.on_step = on_step

  def update(anim):
    if anim.done:
      anim.cell = anim.path[-1]
    else:
      path_pos = anim.time / anim.period
      path_index = int(path_pos)
      step_pos = path_pos - path_index
      if step_pos == 0:
        anim.on_step and anim.on_step(anim.path[path_index])
      if path_index + 1 == len(anim.path):
        anim.end()
      else:
        anim.next_cell = anim.path[path_index + 1]
        from_x, from_y = anim.path[path_index]
        to_x, to_y = anim.next_cell
        dist_x = to_x - from_x
        dist_y = to_y - from_y
        anim.facing = (dist_x and dist_x / abs(dist_x), dist_y and dist_y / abs(dist_y))
        anim.cell = (lerp(from_x, to_x, step_pos), lerp(from_y, to_y, step_pos))
      super().update()
    return anim.cell
