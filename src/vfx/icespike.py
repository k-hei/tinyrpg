from random import randint
from vfx import Vfx
from config import TILE_SIZE
from anims.frame import FrameAnim
from anims.pause import PauseAnim
from lib.sprite import Sprite
from colors.palette import BLACK, WHITE, CYAN
from lib.filters import replace_color
import assets
from vfx.icepiece import IcePieceVfx
from vfx.particle import ParticleVfx
from vfx.smoke import SmokeVfx
from vfx.snowdrift import SnowdriftVfx

class IceSpikeVfx(Vfx):
  def __init__(fx, cell, delay=0, color=CYAN, on_connect=None, on_end=None, *args, **kwargs):
    x, y = cell
    super().__init__(
      kind=None,
      pos=((x + 0.5) * TILE_SIZE, (y + 1) * TILE_SIZE),
      *args,
      **kwargs
    )
    fx.cell = cell
    fx.delay = delay
    fx.color = color
    fx.on_connect = on_connect
    fx.on_end = on_end
    fx.anims = [
      FrameAnim(
        frames=assets.sprites["fx_icespike"],
        duration=30,
        delay=fx.delay
      ),
      PauseAnim(duration=30)
    ]

  def update(fx, *_):
    if not fx.done and not fx.anims:
      fx.init()
    fx_x, fx_y = fx.pos
    fx_y -= TILE_SIZE // 2
    anim = fx.anims[0]
    if anim.done:
      fx.anims.remove(anim)
      if not fx.anims:
        fx.on_end and fx.on_end()
        fx.done = True
        return [IcePieceVfx(
          pos=(fx_x, fx_y),
          color=fx.color
        ) for _ in range(randint(3, 4))]
      elif fx.on_connect:
        fx.on_connect()
        return [
          *([SnowdriftVfx(cell=fx.cell) for i in range(5)]),
          *([SmokeVfx(cell=fx.cell) for i in range(7)]),
          *[ParticleVfx(
            pos=(fx_x, fx_y),
            color=WHITE,
            linger=True
          ) for _ in range(randint(20, 30))]
        ]
      else:
        return []
    else:
      anim.update()
      if type(anim) is FrameAnim and anim.time > 5 and anim.time % 4 == 0:
        return [SmokeVfx(cell=fx.cell)]

  def view(fx):
    fx_anim = fx.anims[0] if fx.anims and type(fx.anims[0]) is FrameAnim else None
    fx_image = fx_anim.frame() if fx_anim else assets.sprites["fx_icespike"][-1]
    if fx_image is None:
      return []
    if fx.color != BLACK:
      fx_image = replace_color(fx_image, BLACK, fx.color)
    return [Sprite(
      image=fx_image,
      pos=fx.pos,
      origin=("center", "bottom"),
      layer="elems"
    )]
