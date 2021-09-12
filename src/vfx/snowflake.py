from vfx import Vfx
import assets
from sprite import Sprite
from filters import replace_color
from colors.palette import BLACK, CYAN
from config import TILE_SIZE
from anims.flicker import FlickerAnim

class SnowflakeVfx(Vfx):
  def __init__(fx, cell, color=CYAN, *args, **kwargs):
    x, y = cell
    super().__init__(
      kind=None,
      pos=((x + 0.5) * TILE_SIZE, (y + 0.5) * TILE_SIZE),
      *args,
      **kwargs
    )
    fx.color = color
    fx.anim = FlickerAnim(duration=60)

  def update(fx, *_):
    if fx.anim.done:
      fx.anim = None
      fx.done = True
    else:
      fx.anim.update()
    return []

  def view(fx):
    if not fx.anim or fx.anim.time % 2:
      return []
    return [Sprite(
      image=replace_color(assets.sprites["fx_snowflake"], BLACK, CYAN),
      pos=fx.pos,
      origin=("center", "center"),
      layer="vfx"
    )]
