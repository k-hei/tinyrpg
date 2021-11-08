from math import sin, pi
from anims import Anim

class SineAnim(Anim):
  period = 0
  amplitude = 1

  def __init__(anim, period=0, amplitude=0, *args, **kwargs):
    super().__init__(*args, **kwargs)
    if period: anim.period = period
    if amplitude: anim.amplitude = amplitude
    anim.pos = 0

  def update(anim):
    time = super().update()
    period = anim.period or 1
    anim.pos = sin(anim.time % period / period * 2 * pi) * anim.amplitude
    return anim.pos
