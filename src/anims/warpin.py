from anims.tween import TweenAnim
from lib.lerp import lerp

class WarpInAnim(TweenAnim):
  def __init__(anim, duration=15, *args, **kwargs):
    super().__init__(duration=duration, *args, **kwargs)
    anim.scale = (0, 3)

  def update(anim):
    t = super().update()
    anim.scale = (t, lerp(3, 1, t))
    return anim.scale
