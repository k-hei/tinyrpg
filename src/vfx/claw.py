from vfx import Vfx
from anims.frame import FrameAnim
import assets
from config import TILE_SIZE
from lib.sprite import Sprite

class ClawVfx(Vfx):
  class ClawAnim(FrameAnim):
    frames = assets.sprites["fx_claw"]
    frames_duration = 7

  def __init__ (fx, cell, delay=0):
    x, y = cell
    super().__init__(kind=None, pos=(x * TILE_SIZE, y * TILE_SIZE))
    fx.anim = ClawVfx.ClawAnim(delay=delay)

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
