import math

class SineAnim:
  def __init__(anim, period, on_end=None):
    anim.done = False
    anim.time = 0
    anim.pos = 0
    anim.period = period
    anim.target = None

  def update(anim):
    anim.time += 1
    anim.pos = math.sin(anim.time % anim.period / anim.period * 2 * math.pi)
    return anim.pos
