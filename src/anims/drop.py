from anims import Anim
from config import WINDOW_HEIGHT, TILE_SIZE

class DropAnim(Anim):
  GRAVITY = 0.2
  BOUNCES = 5

  def __init__(anim, y=(WINDOW_HEIGHT / 2 + TILE_SIZE), *args, **kwargs):
    super().__init__(*args, **kwargs)
    anim.y = y
    anim.vel = 0
    anim.bounces = 0

  def update(anim):
    if anim.done:
      return anim.dest
    time = super().update()
    if time == 0:
      return anim.y
    if anim.bounces == 0:
      anim.y -= anim.vel
      anim.vel += DropAnim.GRAVITY
    elif anim.y == 0:
      anim.y = 1
    elif anim.y == 1:
      anim.y = 0
    if anim.y <= 0:
      anim.y = 0
      anim.bounces += 1
    if anim.bounces == DropAnim.BOUNCES:
      anim.end()
    return anim.y
