from random import randint
from pygame import Surface, SRCALPHA
from vfx import Vfx
from vfx.particle import ParticleVfx
from anims.frame import FrameAnim
from sprite import Sprite
import assets
from filters import replace_color
from colors.palette import BLACK, RED
from config import TILE_SIZE

class LinenVfx(Vfx):
  class LinenAnim(FrameAnim):
    frames_duration = 5

  def __init__(fx, src, dest, color=RED, *args, **kwargs):
    x, y = src
    super().__init__(
      kind=None,
      pos=((x + 0.5) * TILE_SIZE, (y + 0.5) * TILE_SIZE),
      *args,
      **kwargs
    )
    fx.color = color
    linen_length = abs(dest[0] - src[0])
    linen_size = int(TILE_SIZE * linen_length)
    linen_frames = []
    for i, src_frame in enumerate(assets.sprites["fx_linen"]):
      dest_frame = Surface((linen_size, linen_size), SRCALPHA)
      dest_size = TILE_SIZE // 2
      while dest_size < linen_size:
        dest_frame.blit(src_frame, (dest_size - TILE_SIZE // 2, dest_size - TILE_SIZE // 2))
        dest_size += TILE_SIZE // 2
      dest_frame.blit(assets.sprites["fx_linentail"][i], (dest_size - TILE_SIZE // 2, dest_size - TILE_SIZE // 2))
      linen_frames.append(dest_frame)
    fx.anim = LinenVfx.LinenAnim(frames=linen_frames * 3)

  def update(fx, *_):
    if fx.anim:
      if fx.anim.done:
        fx.anim = None
        fx.done = True
      else:
        fx.anim.update()

  def view(fx):
    if fx.done or not fx.anim.frame():
      return []
    fx_image = fx.anim.frame()
    if fx.color != BLACK:
      fx_image = replace_color(fx_image, BLACK, fx.color)
    return [Sprite(
      image=fx_image,
      pos=fx.pos,
      layer="vfx",
    )]
