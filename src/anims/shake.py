from anims import Anim

class ShakeAnim(Anim):
  def __init__(anim, *args, **kwargs):
    super().__init__(*args, **kwargs)
    anim.offset = 0

  def update(anim):
    time = super().update()
    if anim.done:
      return 0
    anim.offset = time // 2 % 2 and -1 or 1
    return anim.offset
