from math import sin, cos, pi
from random import random, randint, choices
from vfx import Vfx
from config import TILE_SIZE
from assets import load as use_assets
from anims.frame import FrameAnim
from sprite import Sprite
from colors.palette import BLACK, WHITE
from filters import replace_color

class ParticleVfx(Vfx):
  def __init__(fx, pos, color=WHITE, *args, **kwargs):
    angle = 2 * pi * random()
    speed = random() + 0.5
    super().__init__(
      kind=None,
      pos=pos,
      vel=(cos(angle) * speed, sin(angle) * speed),
      *args,
      **kwargs
    )
    fx.color = color
    fx.blinking = randint(0, 1)
    fx.anim = None

  def init(fx):
    assets = use_assets()
    fx.anim = FrameAnim(
      frames=[replace_color(s, BLACK, fx.color) for s in assets.sprites["fx_particle"]],
      duration=30
    )

  def update(fx):
    if not fx.done and not fx.anim:
      fx.init()
    fx_x, fx_y = fx.pos
    vel_x, vel_y = fx.vel
    fx.pos = (fx_x + vel_x, fx_y + vel_y)
    if fx.anim.done:
      fx.anim = None
      fx.done = True
    else:
      fx.anim.update()
    return []

  def view(fx):
    if not fx.anim or fx.blinking and fx.anim.time % 2:
      return []
    return [Sprite(
      image=fx.anim.frame,
      pos=fx.pos,
      origin=("center", "center"),
      layer="vfx"
    )]
