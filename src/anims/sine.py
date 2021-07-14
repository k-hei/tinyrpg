from math import sin, pi
from anims import Anim

class SineAnim(Anim):
  def __init__(anim, period, amplitude=1, *args, **kwargs):
    super().__init__(*args, **kwargs)
    anim.period = period
    anim.amplitude = amplitude
    anim.pos = 0

  def update(anim):
    time = super().update()
    anim.pos = sin(anim.time % anim.period / anim.period * 2 * pi) * anim.amplitude
    return anim.pos
