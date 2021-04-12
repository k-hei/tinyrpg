from anims.flicker import FlickerAnim

class AwakenAnim(FlickerAnim):
  def __init__(anim, duration, target, on_end=None):
    super().__init__(duration, target, on_end)
