from anims.tween import TweenAnim
import lib.vector as vector

class MoveAnim(TweenAnim):
  def __init__(anim, src, dest, speed, *args, **kwargs):
    super().__init__(
      duration=vector.distance(src, dest) // speed,
      *args, **kwargs
    )
    anim.src = src
    anim.dest = dest
    anim.pos = src

  def update(anim):
    t = super().update()
    if anim.done:
      anim.pos = anim.dest
      return anim.dest
    anim.pos = vector.lerp(anim.src, anim.dest, t)
    return anim.pos
