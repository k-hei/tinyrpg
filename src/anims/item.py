from anims import Anim

class ItemAnim(Anim):
  def __init__(anim, item, *args, **kwargs):
    super().__init__(*args, **kwargs)
    anim.item = item
