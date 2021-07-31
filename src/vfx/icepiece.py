from random import random, choices
from vfx import Vfx
from config import TILE_SIZE
from assets import load as use_assets
from anims.flicker import FlickerAnim
from sprite import Sprite
from colors.palette import BLACK, CYAN
from filters import replace_color

class IcePieceVfx(Vfx):
  def __init__(fx, pos, color=CYAN, *args, **kwargs):
    super().__init__(
      kind=None,
      pos=pos,
      vel=(random() * 2 - 1, -2 + random() / 2),
      *args,
      **kwargs
    )
    fx.color = color
    fx.gravity = 0.2
    fx.image = None
    fx.anim = []

  def init(fx):
    assets = use_assets()
    fx.image = assets.sprites[choices(["fx_icepiece", "fx_icechunk"], weights=[2, 1], k=1)[0]]
    if fx.color != BLACK:
      fx.image = replace_color(fx.image, BLACK, fx.color)
    fx.anim = FlickerAnim(duration=30)

  def update(fx, *_):
    fx_x, fx_y = fx.pos
    vel_x, vel_y = fx.vel
    fx.pos = (fx_x + vel_x, fx_y + vel_y)
    fx.vel = (vel_x, vel_y + fx.gravity)
    if not fx.done and not fx.anim:
      fx.init()
    if fx.anim.done:
      fx.anim = None
      fx.done = True
    else:
      fx.anim.update()
    return []

  def view(fx):
    if not fx.anim or not fx.anim.visible:
      return []
    return [Sprite(
      image=fx.image,
      pos=fx.pos,
      origin=("center", "center"),
      layer="vfx"
    )]
