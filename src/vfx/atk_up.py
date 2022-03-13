from vfx.anim import AnimVfx
from anims.frame import FrameAnim
import assets

class AtkUpVfx(AnimVfx):
  class Anim(FrameAnim):
    frames = assets.sprites["fx_atkup"] * 2
    frames_duration = 4
