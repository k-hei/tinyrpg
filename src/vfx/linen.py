from math import sqrt
from random import randint
from pygame import Surface, SRCALPHA
from pygame.transform import rotate
from vfx import Vfx
from vfx.particle import ParticleVfx
from anims.frame import FrameAnim
from lib.sprite import Sprite
import assets
from lib.filters import replace_color
from colors.palette import BLACK, WHITE, RED
from config import TILE_SIZE

class LinenVfx(Vfx):
  class LinenAnim(FrameAnim):
    frames_duration = 3

  def __init__(fx, src, dest, color=RED, on_connect=None, on_end=None, *args, **kwargs):
    src_x, src_y = src
    dest_x, dest_y = dest
    super().__init__(
      kind=None,
      pos=((src_x + 0.5) * TILE_SIZE, (src_y + 0.5) * TILE_SIZE),
      *args,
      **kwargs
    )
    dist_x = dest_x - src_x
    dist_y = dest_y - src_y
    normal = (dist_x < 0 and -1 or 1, dist_y < 0 and -1 or 1)
    linen_length = abs(dist_x)
    linen_size = int(TILE_SIZE * linen_length)
    linen_frames = []
    linen_rotation = {
      (1, 1): 0,
      (-1, 1): 90,
      (-1, -1): 180,
      (1, -1): 270,
    }[normal]
    linen_origin = {
      (1, 1): ("left", "top"),
      (-1, 1): ("right", "top"),
      (1, -1): ("left", "bottom"),
      (-1, -1): ("right", "bottom"),
    }[normal]
    retract_frames = []
    for frame_size in range(0, linen_size + 1, TILE_SIZE // 2):
      linen_chunk = []
      for i, src_frame in enumerate(assets.sprites["fx_linen"]):
        dest_frame = Surface((frame_size, frame_size), SRCALPHA)
        dest_size = TILE_SIZE // 2
        while dest_size < frame_size:
          dest_frame.blit(src_frame, (dest_size - TILE_SIZE // 2, dest_size - TILE_SIZE // 2))
          dest_size += TILE_SIZE // 2
        tail_frame = assets.sprites["fx_linentail"][i]
        dest_frame.blit(tail_frame, (dest_size - TILE_SIZE // 2, dest_size - TILE_SIZE // 2))
        if linen_rotation:
          dest_frame = rotate(dest_frame, linen_rotation)
        linen_chunk.append(dest_frame)
        if frame_size < linen_size:
          retract_frames.append(dest_frame)
          break
      linen_frames += linen_chunk
    while len(linen_frames) < 9:
      linen_frames += linen_chunk
    linen_frames += reversed(retract_frames)

    fx.dest = ((dest_x + 0.5) * TILE_SIZE, (dest_y + 0.5) * TILE_SIZE)
    fx.color = color
    fx.on_connect = on_connect
    fx.on_end = on_end
    fx.length = len(retract_frames)
    fx.origin = linen_origin
    fx.anim = LinenVfx.LinenAnim(frames=linen_frames)

  def update(fx, *_):
    if fx.anim:
      if fx.anim.done:
        fx.anim = None
        fx.done = True
        fx.on_end and fx.on_end()
      else:
        fx.anim.update()
        if fx.on_connect and fx.anim.frame_index == fx.length:
          on_connect = fx.on_connect
          fx.on_connect = None
          if on_connect():
            return [ParticleVfx(
              pos=fx.dest,
              color=fx.color if randint(0, 1) and fx.color != BLACK else WHITE
            ) for _ in range(randint(10, 15))]
          else:
            return []

  def view(fx):
    if fx.done or not fx.anim.frame():
      return []
    fx_image = fx.anim.frame()
    if fx.color != BLACK:
      fx_image = replace_color(fx_image, BLACK, fx.color)
    return [Sprite(
      image=fx_image,
      pos=fx.pos,
      origin=fx.origin,
      layer="vfx",
    )]
