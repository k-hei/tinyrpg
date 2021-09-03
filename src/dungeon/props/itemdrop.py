from math import sqrt
from dungeon.props import Prop
from sprite import Sprite
from anims.tween import TweenAnim
from config import TILE_SIZE

class ItemDrop(Prop):
  class ThrownAnim(TweenAnim):
    speed = 8 / TILE_SIZE

    def __init__(anim, src, dest, *args, **kwargs):
      super().__init__(*args, **kwargs)
      src_x, src_y = src
      dest_x, dest_y = dest
      dist_x, dist_y = (dest_x - src_x, dest_y - src_y)
      dist = sqrt(dist_x * dist_x + dist_y * dist_y)
      anim.offset = (0, 0)
      anim.normal = (dist_x / dist, dist_y / dist)
      anim.duration = int(dist / anim.speed)

    def update(anim):
      super().update()
      x, y = anim.offset
      norm_x, norm_y = anim.normal
      anim.offset = (x + norm_x * anim.speed, y + norm_y * anim.speed)
      return anim.offset

  def __init__(drop, contents):
    drop.item = contents

  def effect(drop, game):
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
