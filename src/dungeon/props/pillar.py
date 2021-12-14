from random import randint
from pygame import Rect
import lib.vector as vector
from lib.sprite import Sprite
from lib.filters import replace_color

from dungeon.props import Prop
from vfx.pillarchunk import PillarChunkVfx
import assets
from colors.palette import WHITE, SAFFRON

class Pillar(Prop):
  solid = True
  static = True
  breakable = True

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
    if pillar.broken:
      return
    pillar.broken = True
    game.stage_view.shake(vertical=True)
    game.vfx.extend([
      PillarChunkVfx(cell=pillar.cell, size=PillarChunkVfx.SIZE_XL),
      PillarChunkVfx(cell=pillar.cell, size=PillarChunkVfx.SIZE_L),
      PillarChunkVfx(cell=pillar.cell, size=PillarChunkVfx.SIZE_M),
      PillarChunkVfx(cell=pillar.cell, size=PillarChunkVfx.SIZE_M),
      PillarChunkVfx(cell=pillar.cell, size=PillarChunkVfx.SIZE_S),
      PillarChunkVfx(cell=pillar.cell, size=PillarChunkVfx.SIZE_S),
    ])

  def view(pillar, anims):
    if pillar.broken:
      pillar_image = assets.sprites["pillar_broken"]
    else:
      pillar_image = assets.sprites["pillar"]
    pillar_image = replace_color(pillar_image, WHITE, SAFFRON)
    return super().view([Sprite(
      image=pillar_image,
      pos=(0, 16),
      layer="elems",
      origin=Sprite.ORIGIN_BOTTOM,
    )], anims)
