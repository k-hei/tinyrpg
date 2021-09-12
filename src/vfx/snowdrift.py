from math import sin, cos, pi
from random import random, randint, choice
from vfx import Vfx
from pygame.transform import rotate
import assets
from sprite import Sprite
from anims import Anim
from filters import replace_color
from colors.palette import BLACK, WHITE, CYAN
from config import TILE_SIZE

class SnowdriftVfx(Vfx):
  def __init__(fx, cell, color=CYAN, angle=None, *args, **kwargs):
    angle = 2 * pi * random() if angle is None else angle
    speed = random() + 1
    col, row = cell
    super().__init__(
      kind=None,
      pos=((col + 0.5) * TILE_SIZE, (row + 0.5) * TILE_SIZE),
      vel=(cos(angle) * speed, sin(angle) * speed),
      *args,
      **kwargs
    )
    fx.color = color
    fx.anim = Anim(duration=90, delay=randint(0, 30))
    fx.rotation = 0
    fx.torque = randint(5, 8) * (randint(0, 1) * 2 - 1)

  def update(fx, *_):
    if fx.anim.time >= 0:
      fx_x, fx_y = fx.pos
      vel_x, vel_y = fx.vel
      fx.pos = (fx_x + vel_x, fx_y + vel_y)
      fx.vel = (vel_x * 0.95, vel_y * 0.95)
      fx.rotation += fx.torque
    if fx.anim.done:
      fx.anim = None
      fx.done = True
    else:
      fx.anim.update()
    return []

  def view(fx):
    if not fx.anim or fx.anim.time > fx.anim.duration / 2 and fx.anim.time % 2:
      return []
    snow_image = assets.sprites["fx_snowflake_small"]
    if fx.color != BLACK:
      snow_image = replace_color(snow_image, BLACK, fx.color)
    if fx.rotation:
      snow_image = rotate(snow_image, fx.rotation // 30 * 30)
    return [Sprite(
      image=snow_image,
      pos=tuple([x // 2 * 2 for x in fx.pos]),
      origin=("center", "center"),
      offset=-16,
      layer="vfx"
    )]
