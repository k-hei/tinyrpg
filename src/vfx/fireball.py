from math import sqrt, cos, sin, atan2, pi
from random import random, choice
from vfx import Vfx
from config import TILE_SIZE
from palette import RED
from anims import Anim
from anims.tween import TweenAnim
from lib.lerp import lerp
from easing.expo import ease_out

class DriftAnim(TweenAnim): pass
class PauseAnim(Anim): pass
class HomeAnim(Anim): pass

class Fireball(Vfx):
  speed = -1
  accel = 1 / 5
  turn_speed = pi / 8

  def __init__(fx, start_pos, target_pos, delay=0, on_end=None):
    super().__init__(None, start_pos)
    fx.start_pos = start_pos
    fx.pos = start_pos
    fx.target_pos = target_pos
    fx.start_angle = angle(start_pos, target_pos)
    fx.angle = fx.start_angle + pi * random() * 0.5 + pi * 0.75
    fx.target_angle = None
    fx.dist = 16 + 16 * random()
    fx.color = RED
    fx.anims = [
      DriftAnim(duration=10, delay=delay),
      PauseAnim(duration=30),
      HomeAnim()
    ]
    fx.on_end=on_end
    fx.done = False

  def update(fx):
    x, y = fx.pos
    anim = fx.anims[0] if fx.anims else None
    if anim:
      t = anim.update()
    if not anim or anim.done:
      fx.anims.remove(anim)
      if len(fx.anims) == 0:
        fx.done = True
        if fx.on_end:
          fx.on_end()
    if type(anim) is DriftAnim:
      t = ease_out(t)
      start_x, start_y = fx.start_pos
      target_x = start_x + cos(fx.angle) * fx.dist
      target_y = start_y + sin(fx.angle) * fx.dist
      x = lerp(start_x, target_x, t)
      y = lerp(start_y, target_y, t)
      if anim.done:
        fx.start_pos = (x, y)
    elif type(anim) is PauseAnim:
      pass
    elif type(anim) is HomeAnim:
      if anim.time == 1:
        fx.target_angle = angle(fx.start_pos, fx.target_pos)
        fx.angle = fx.target_angle
      speed = fx.speed + fx.accel * anim.time
      if dist(fx.pos, fx.target_pos) <= speed:
        fx.pos = fx.target_pos
        anim.done = True
      if fx.angle > fx.target_angle:
        fx.angle -= fx.turn_speed
      elif fx.angle < fx.target_angle:
        fx.angle += fx.turn_speed
      x += cos(fx.angle) * speed
      y += sin(fx.angle) * speed
    fx.pos = (x, y)

def angle(a, b):
  x1, y1 = a
  x2, y2 = b
  return atan2(y2 - y1, x2 - x1)

def dist(a, b):
  x1, y1 = a
  x2, y2 = b
  return sqrt(pow(x2 - x1, 2) + pow(y2 - y1, 2))
