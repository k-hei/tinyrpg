from vfx import Vfx
from anims.frame import FrameAnim
import assets
from config import TILE_SIZE
from lib.sprite import Sprite


class AnimVfx(Vfx):

  class Anim(FrameAnim):
      pass

  def __init__ (fx, cell, delay=0, on_end=None):
    super().__init__(
        kind=None,
        pos=tuple([(x + 0.5) * TILE_SIZE for x in cell])
    )
    fx.anim = fx.Anim(delay=delay, on_end=on_end)

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
      origin=Sprite.ORIGIN_CENTER,
      layer="vfx",
    )]
