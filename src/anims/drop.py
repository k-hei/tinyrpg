from anims import Anim

class DropAnim(Anim):
  GRAVITY = 0.2
  BOUNCES = 5

  def __init__(anim, y, *args, **kwargs):
    super().__init__(*args, **kwargs)
    anim.y = y
    anim.vel = 0
    anim.bounces = 0

  def update(anim):
    if anim.done:
      return anim.dest
    super().update()
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
      anim.done = True
    return anim.y
