from math import sqrt
from dungeon.props import Prop
from sprite import Sprite
from anims.offsetmove import OffsetMoveAnim
from config import TILE_SIZE

class ItemDrop(Prop):
  ThrownAnim = OffsetMoveAnim

  def __init__(drop, contents):
    drop.item = contents

  def effect(drop, game, actor):
    if actor is game.hero:
      game.obtain(
        item=drop.item,
        target=drop,
        on_end=lambda: game.floor.remove_elem(drop)
      )

  def view(drop, anims):
    anim_group = [a for a in anims[0] if a.target is drop] if anims else []
    offset_x, offset_y = (0, -8)
    offset_layer = "elems"
    for anim in anim_group:
      if type(anim) is ItemDrop.ThrownAnim:
        col, row = anim.offset
        offset_x += col * TILE_SIZE
        offset_y += row * TILE_SIZE + (1 - anim.pos) * -16
        offset_layer = "vfx"
    return super().view([Sprite(
      image=drop.item().render(),
      pos=(offset_x, offset_y),
      layer=offset_layer
    )], anims)
