from vfx.anim import AnimVfx
from anims.frame import FrameAnim
import assets

class DefUpVfx(AnimVfx):
  class Anim(FrameAnim):
    frames = assets.sprites["fx_defup"]
    frames_duration = 4
