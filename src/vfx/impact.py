from vfx import Vfx
from anims.frame import FrameAnim
import assets
from config import TILE_SIZE
from sprite import Sprite

class ImpactVfx(Vfx):
  class ImpactAnim(FrameAnim):
    frames = assets.sprites["fx_impact"]
    frames_duration = 3

  def __init__ (fx, cell, delay=0):
    x, y = cell
    super().__init__(kind=None, pos=(x * TILE_SIZE, y * TILE_SIZE))
    fx.anim = ImpactVfx.ImpactAnim(delay=delay)

  def update(fx, _):
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
