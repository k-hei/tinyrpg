from math import pi, sin, cos
from vfx import Vfx
from vfx.particle import ParticleVfx
from lib.cell import add as add_vector
from easing.circ import ease_out
import assets
from anims import Anim
from anims.flicker import FlickerAnim
from sprite import Sprite
from filters import replace_color
from colors.palette import BLACK, CYAN
from config import TILE_SIZE

class EnterAnim(Anim): pass

class IceEmblemVfx(Vfx):
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
    fx.anims = [
      EnterAnim(duration=100, delay=delay),
      FlickerAnim(duration=45)
    ]

  def update(fx, *_):
    anim = fx.anims[0]
    if anim:
      if anim.done:
        fx.anims.pop(0)
        if not fx.anims:
          fx.done = True
      else:
        anim.update()
        if type(anim) is EnterAnim and anim.time >= 0:
          return [
            ParticleVfx(
              pos=add_vector(fx.pos, (0, -TILE_SIZE)),
              color=fx.color,
              offset=4,
            )
          ]

  def view(fx):
    if not fx.anims or fx.anims[0].time < 0:
      return []

    anim = fx.anims[0]
    offset_y = sin((anim.time - 15) % 90 / 90 * 2 * pi) * 2
    if type(anim) is EnterAnim:
      if anim.time < 15:
        offset_y = (1 - ease_out(anim.time / 15)) * TILE_SIZE / 4
      w = 1 - (cos(min(40, anim.time) % 16 / 16 * 2 * pi) + 1) / 2
    elif type(anim) is FlickerAnim:
      if not anim.visible:
        return []
      t = max(0, anim.time - 30) / (anim.duration - 30)
      offset_y += t * -TILE_SIZE / 4
      w = 1 - t

    emblem_image = assets.sprites["ice_emblem"]
    if fx.color != BLACK:
      emblem_image = replace_color(emblem_image, BLACK, fx.color)
    return [Sprite(
      image=emblem_image,
      pos=add_vector(fx.pos, (0, -TILE_SIZE + offset_y)),
      size=(emblem_image.get_width() * w, emblem_image.get_height()),
      origin=("center", "center"),
      layer="vfx"
    )]
