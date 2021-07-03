from anims import Anim

class FlickerAnim(Anim):
  def __init__(anim, *args, **kwargs):
    super().__init__(*args, **kwargs)
    anim.visible = False

  def update(anim):
    time = super().update()
    if anim.done:
      return False
    anim.visible = time % 2 == 0
    return anim.visible
