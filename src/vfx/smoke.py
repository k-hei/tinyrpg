from math import sin, cos, pi
from random import random, randint, choice
from vfx import Vfx
import assets
from sprite import Sprite
from anims import Anim
from filters import replace_color
from colors.palette import BLACK, WHITE
from config import TILE_SIZE

class SmokeVfx(Vfx):
  def __init__(fx, cell=None, pos=None, color=WHITE, angle=None, size=None, *args, **kwargs):
    angle = 2 * pi * random() if angle is None else angle
    speed = random() + 0.25
    if not pos:
      col, row = cell
      pos = ((col + 0.5) * TILE_SIZE, (row + 1) * TILE_SIZE)
    super().__init__(
      kind=None,
      pos=pos,
      vel=(cos(angle) * speed, sin(angle) * speed / 2),
      *args,
      **kwargs
    )
    fx.color = color
    fx.size = size or choice(["large", "small"])
    fx.anim = Anim(duration=90, delay=randint(0, 30))

  def update(fx, *_):
    if fx.anim.time >= 0:
      fx_x, fx_y = fx.pos
      vel_x, vel_y = fx.vel
      fx.pos = (fx_x + vel_x, fx_y + vel_y)
      fx.vel = (vel_x * 0.975, vel_y * 0.975)
    if fx.anim.done:
      fx.anim = None
      fx.done = True
    else:
      fx.anim.update()
    return []

  def view(fx):
    if not fx.anim or fx.anim.time > fx.anim.duration / 2 and fx.anim.time % 2:
      return []
    return [Sprite(
      image=assets.sprites[f"fx_smoke_{fx.size}"],
      pos=tuple([x // 2 * 2 for x in fx.pos]),
      origin=("center", "center"),
      offset=-16,
      layer="vfx"
    )]
