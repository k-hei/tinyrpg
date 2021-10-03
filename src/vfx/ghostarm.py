from random import randint
from vfx import Vfx
from config import TILE_SIZE
from anims.frame import FrameAnim
from anims.pause import PauseAnim
from sprite import Sprite
from colors.palette import BLACK, WHITE, RED
from lib.filters import replace_color
import assets
from vfx.particle import ParticleVfx

class GhostArmVfx(Vfx):
  def __init__(fx, cell, delay=0, color=RED, on_connect=None, *args, **kwargs):
    x, y = cell
    super().__init__(
      kind=None,
      pos=((x + 0.5) * TILE_SIZE, (y + 1) * TILE_SIZE),
      *args,
      **kwargs
    )
    fx.delay = delay
    fx.color = color
    fx.on_connect = on_connect
    fx.anims = [
      FrameAnim(
        frames=[
          assets.sprites["ghostarm_shrink"][0],
          *assets.sprites["ghostarm"],
          *assets.sprites["ghostarm"],
          assets.sprites["ghostarm_shrink"][0],
          assets.sprites["ghostarm_shrink"][1]
        ],
        frames_duration=[4, *([2] * len(assets.sprites["ghostarm"]) * 2), 6, 6],
        delay=fx.delay
      )
    ]
    fx.connected = False

  def update(fx, *_):
    if not fx.done and not fx.anims:
      fx.init()
    fx_x, fx_y = fx.pos
    fx_y -= TILE_SIZE // 2
    fx_anim = fx.anims[0]
    if fx_anim.done:
      fx.done = True
    else:
      fx_anim.update()
      if not fx.connected and fx_anim.frame_index == 1 and fx.on_connect:
        fx.connected = True
        if fx.on_connect():
          return [ParticleVfx(
            pos=(fx_x, fx_y),
            color=fx.color if randint(0, 1) and fx.color != BLACK else WHITE
          ) for _ in range(randint(10, 15))]
    return []

  def view(fx):
    fx_anim = fx.anims and fx.anims[0]
    fx_image = fx_anim.frame()
    if fx_image is None:
      return []
    if fx.color != BLACK:
      fx_image = replace_color(fx_image, BLACK, fx.color)
    return [Sprite(
      image=fx_image,
      pos=fx.pos,
      origin=("center", "bottom"),
      layer="vfx"
    )]
