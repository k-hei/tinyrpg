from anims.tween import TweenAnim

class ItemAnim(TweenAnim):
  def __init__(anim, duration, target, item, delay=0, on_end=None):
    super().__init__(duration, delay, target, on_end)
    anim.item = item
