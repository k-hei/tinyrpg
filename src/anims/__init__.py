from anims.attack import AttackAnim
from anims.flicker import FlickerAnim
from anims.awaken import AwakenAnim
from anims.move import MoveAnim
from anims.flinch import FlinchAnim
from anims.pause import PauseAnim

class Anim:
  def __init__(anim, duration=None, on_end=None):
    anim.done = False
    anim.time = 0
    anim.duration = duration
    anim.on_end = on_end

  def update(anim):
    if anim.done:
      return -1
    anim.time += 1
    if anim.time == anim.duration:
      anim.done = True
      if anim.on_end:
        anim.on_end()
    return anim.time
