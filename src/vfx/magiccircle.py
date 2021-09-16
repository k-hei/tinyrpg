from math import pi, sin, cos
from pygame.transform import rotate
from lib.cell import add as add_vector
from easing.circ import ease_out
from filters import replace_color

from vfx import Vfx
from vfx.particle import ParticleVfx
import assets
from anims import Anim
from sprite import Sprite
from colors.palette import BLACK, CYAN
from config import TILE_SIZE

class MagicCircleVfx(Vfx):
  def __init__(fx, cell, color=CYAN, delay=0, *args, **kwargs):
    col, row = cell
    pos = ((col + 0.5) * TILE_SIZE, (row + 0.5) * TILE_SIZE)
    super().__init__(
      kind=None,
      pos=pos,
      *args,
      **kwargs
    )
    fx.color = color
    fx.anim = Anim(duration=90)

  def update(fx, *_):
    if fx.anim.done:
      fx.anim = None
      fx.done = True
    else:
      fx.anim.update()

  def view(fx):
    if not fx.anim or fx.anim.time % 2:
      return []
    fx_image = assets.sprites["magic_circle"]
    if fx.color != BLACK:
      fx_image = replace_color(fx_image, BLACK, fx.color)
    fx_image = rotate(fx_image, fx.anim.time // 5 * 5)
    return [Sprite(
      image=fx_image,
      pos=add_vector(fx.pos, (0, TILE_SIZE / 3)),
      size=(fx_image.get_width(), fx_image.get_height() * 2 / 3),
      origin=("center", "center"),
      offset=-16,
      layer="elems"
    )]
