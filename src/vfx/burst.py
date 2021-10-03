from random import randint
from vfx import Vfx
from vfx.particle import ParticleVfx
from anims.frame import FrameAnim
import assets
from sprite import Sprite
from config import TILE_SIZE
from lib.filters import replace_color
from colors.palette import BLACK, WHITE

class BurstVfx(Vfx):
  class BurstAnim(FrameAnim):
    frames = assets.sprites["fx_burst"]
    frames_duration = 3

  def __init__ (fx, cell, color=BLACK, delay=0):
    x, y = cell
    super().__init__(kind=None, pos=(x * TILE_SIZE, y * TILE_SIZE), color=color)
    fx.anim = BurstVfx.BurstAnim(delay=delay)

  def update(fx, *_):
    if fx.anim:
      if fx.anim.done:
        fx.anim = None
        fx.done = True
      else:
        fx.anim.update()
    if fx.anim and fx.anim.time == 1:
      return [ParticleVfx(
        pos=tuple([x + TILE_SIZE / 2 for x in fx.pos]),
        color=fx.color if randint(0, 1) and fx.color != BLACK else WHITE
      ) for _ in range(randint(10, 15))]

  def view(fx):
    if fx.done or not fx.anim.frame():
      return []
    fx_image = fx.anim.frame()
    if fx.color != BLACK:
      fx_image = replace_color(fx_image, BLACK, fx.color)
    return [Sprite(
      image=fx_image,
      pos=fx.pos,
      layer="vfx",
    )]
