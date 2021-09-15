from math import sin, cos, pi
from random import random, randint
from lib.cell import add as add_vector

from vfx import Vfx
import assets
from anims.frame import FrameAnim
from anims.flicker import FlickerAnim
from sprite import Sprite
from filters import replace_color
from colors.palette import BLACK, WHITE
from config import TILE_SIZE

class ParticleVfx(Vfx):
  def __init__(fx, pos=None, cell=None, offset=0, color=WHITE, linger=False, *args, **kwargs):
    angle = 2 * pi * random()
    speed = random() + 1
    if cell:
      col, row = cell
      pos = ((col + 0.5) * TILE_SIZE, (row + 0.5) * TILE_SIZE)
    if offset:
      pos = add_vector(pos, (
        cos(angle) * offset,
        sin(angle) * offset
      ))
    super().__init__(
      kind=None,
      pos=pos,
      vel=(
        cos(angle) * speed,
        sin(angle) * speed
      ),
      *args,
      **kwargs
    )
    fx.offset = offset
    fx.color = color
    fx.blinking = False if linger else randint(0, 1)
    fx.linger = linger
    fx.anim = None

  def init(fx):
    fx.anim = FrameAnim(
      frames=[replace_color(s, BLACK, fx.color) for s in assets.sprites["fx_particle"]],
      duration=45,
      delay=randint(0, 45) if not fx.offset else 0
    )

  def update(fx, *_):
    if not fx.done and not fx.anim:
      fx.init()
    if fx.anim.time >= 0:
      fx_x, fx_y = fx.pos
      vel_x, vel_y = fx.vel
      fx.pos = (fx_x + vel_x, fx_y + vel_y)
      if type(fx.anim) is FrameAnim:
        friction = 0.95 if fx.linger else 0.925
        fx.vel = (vel_x * friction, vel_y * friction)
    if fx.anim.done:
      if fx.linger:
        fx.linger = False
        fx.anim = FlickerAnim(duration=randint(90, 150))
        fx.vel = (0, 0.1)
      else:
        fx.anim = None
        fx.done = True
    else:
      fx.anim.update()
    return []

  def view(fx):
    if not fx.anim or (fx.blinking or type(fx.anim) is FlickerAnim) and fx.anim.time % 2:
      return []
    fx_image = fx.anim.frame() if type(fx) is FrameAnim else replace_color(assets.sprites["fx_particle_small"], BLACK, fx.color)
    return [Sprite(
      image=fx_image,
      pos=fx.pos,
      origin=("center", "center"),
      layer="vfx"
    )]
