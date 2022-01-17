import random
import lib.vector as vector
from lib.sprite import Sprite
from lib.filters import replace_color

from vfx import Vfx
from anims import Anim
import assets
from colors.palette import WHITE, SAFFRON
from config import TILE_SIZE

class PillarChunkVfx(Vfx):
  SIZE_XL = "extra_large"
  SIZE_L = "large"
  SIZE_M = "medium"
  SIZE_S = "small"
  GRAVITY = 0.1

  def resolve_sprite(size):
    size_map = {
      PillarChunkVfx.SIZE_XL: "chunk_l",
      PillarChunkVfx.SIZE_L: "chunk_s",
      PillarChunkVfx.SIZE_M: "bit_l",
      PillarChunkVfx.SIZE_S: "bit_s"
    }
    return (
      f"tomb_pillar_{size_map[size]}"
    ) if size in size_map else None

  def __init__(fx, cell, size=SIZE_M, *args, **kwargs):
    super().__init__(
      kind=None,
      pos=vector.scale(vector.add(cell, (0.5, 0.5)), TILE_SIZE),
      vel=(random.uniform(-1, 1), random.uniform(-1, -2)),
      *args,
      **kwargs
    )
    fx.size = size
    fx.anim = Anim(duration=random.randint(30, 60))

  def update(fx, *_):
    if not fx.anim:
      return []

    if fx.anim.done:
      fx.anim = None
      fx.done = True
    else:
      fx.anim.update()

    fx.vel = vector.add(fx.vel, (0, PillarChunkVfx.GRAVITY))
    fx.pos = vector.add(fx.pos, fx.vel)

    return []

  def view(fx):
    if not fx.anim or fx.anim.time >= fx.anim.duration / 2 and fx.anim.time % 2:
      return []

    fx_id = PillarChunkVfx.resolve_sprite(fx.size)
    if not fx_id:
      return []

    fx_image = assets.sprites[fx_id]
    fx_image = replace_color(fx_image, old_color=WHITE, new_color=SAFFRON)
    return [Sprite(
      image=fx_image,
      pos=fx.pos,
      origin=Sprite.ORIGIN_CENTER,
      layer="vfx"
    )]
