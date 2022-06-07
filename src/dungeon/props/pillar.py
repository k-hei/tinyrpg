from random import randint
from pygame import Rect
import lib.vector as vector
from lib.sprite import Sprite
from lib.filters import replace_color

from dungeon.props import Prop
from vfx.pillarchunk import PillarChunkVfx
import assets
from colors.palette import WHITE

class Pillar(Prop):
  solid = True
  static = True
  breakable = True
  image = assets.sprites["pillar"]

  def __init__(pillar, broken=None):
    super().__init__()
    pillar.broken = broken if broken is not None else not randint(0, 2)

  @property
  def rect(pillar):
    if pillar._rect is None and pillar.pos:
      pillar._rect = Rect(
        vector.subtract(pillar.pos, (8, 0)),
        (16, 16)
      )
    return pillar._rect

  def crush(pillar, game):
    create_pillar_chunk = lambda size: PillarChunkVfx(
      cell=pillar.cell,
      color=pillar.color,
      size=size,
    )

    game.stage_view.shake(vertical=True)
    game.vfx.extend([
      *([create_pillar_chunk(size=PillarChunkVfx.SIZE_XL)] if not pillar.broken else []),
      create_pillar_chunk(size=PillarChunkVfx.SIZE_L),
      create_pillar_chunk(size=PillarChunkVfx.SIZE_M),
      create_pillar_chunk(size=PillarChunkVfx.SIZE_M),
      create_pillar_chunk(size=PillarChunkVfx.SIZE_S),
      create_pillar_chunk(size=PillarChunkVfx.SIZE_S),
    ])

    pillar.broken = True

  def view(pillar, anims):
    if pillar.broken:
      pillar_image = assets.sprites["pillar_broken"]
    else:
      pillar_image = assets.sprites["pillar"]
    pillar_image = replace_color(pillar_image, WHITE, pillar.color)
    return super().view([Sprite(
      image=pillar_image,
      pos=(0, 16),
      layer="elems",
      origin=Sprite.ORIGIN_BOTTOM,
    )], anims)
