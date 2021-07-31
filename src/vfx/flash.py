from pygame import Surface, Color, SRCALPHA
from vfx import Vfx
from sprite import Sprite
from colors.palette import WHITE
from config import WINDOW_SIZE

class FlashVfx(Vfx):
  duration = 6

  def __init__(fx, color=WHITE, *args, **kwargs):
    super().__init__(
      kind=None,
      pos=(0, 0),
      *args,
      **kwargs
    )
    fx.time = 0
    fx.surface = Surface(WINDOW_SIZE)
    fx.surface.fill(color)
    fx.surface_half = Surface(WINDOW_SIZE, SRCALPHA)
    fx.surface_half.fill(Color(*color, 0x7F))

  def update(fx, *_):
    if fx.done:
      return
    fx.time += 1
    if fx.time == fx.duration:
      fx.done = True

  def view(fx):
    return [Sprite(
      image=(fx.time >= fx.duration // 2 and fx.surface or fx.surface_half),
      pos=(0, 0),
      layer="ui"
    )]
