from anims import Anim
from config import WINDOW_HEIGHT, TILE_SIZE

class FallAnim(Anim):
  def __init__(anim, y, gravity=0.2, *args, **kwargs):
    super().__init__(*args, **kwargs)
    anim.y = 0
    anim.dest = WINDOW_HEIGHT // 2 + TILE_SIZE
    anim.gravity = gravity
    anim.vel = 0

  def update(anim):
    if anim.done:
      return anim.dest
    time = super().update()
    if time == 0:
      return anim.y
    anim.vel += anim.gravity
    anim.y += anim.vel
    if anim.y >= anim.dest:
      anim.end()
    return anim.y
