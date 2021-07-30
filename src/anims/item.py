from math import inf
from anims import Anim

class ItemAnim(Anim):
  def __init__(anim, item, duration=inf, *args, **kwargs):
    super().__init__(duration=duration, *args, **kwargs)
    anim.item = item
