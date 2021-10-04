from vfx import Vfx
from anims.frame import FrameAnim
import assets
from config import TILE_SIZE
from lib.sprite import Sprite

class GeyserVfx(Vfx):
  class GeyserAnim(FrameAnim):
    frames = assets.sprites["fx_geyser"]
    frames_duration = 4

  def __init__ (fx, cell, delay=0):
    super().__init__(kind=None, pos=tuple([x * TILE_SIZE for x in cell]))
    fx.anim = GeyserVfx.GeyserAnim(delay=delay)

  def update(fx, *_):
    if fx.anim:
      if fx.anim.done:
        fx.anim = None
        fx.done = True
      else:
        fx.anim.update()

  def view(fx):
    if fx.done or not fx.anim.frame():
      return []
    return [Sprite(
      image=fx.anim.frame(),
      pos=fx.pos,
      layer="vfx",
    )]
