from pygame import Rect
from dungeon.props import Prop
from lib.sprite import Sprite
import lib.vector as vector
from config import TILE_SIZE
from anims.offsetmove import OffsetMoveAnim

class ItemDrop(Prop):
  ThrownAnim = OffsetMoveAnim
  active = True

  def __init__(drop, contents, *args, **kwargs):
    super().__init__(*args, **kwargs)
    drop.item = contents
    drop.obtained = False

  @property
  def rect(drop):
    if drop._rect is None and drop.pos:
      drop._rect = Rect(
        vector.subtract(drop.pos, (4, 4)),
        (8, 8)
      )
    return drop._rect

  def effect(drop, game, actor):
    if actor is not game.hero:
      return None

    if drop.obtained:
      return False

    obtained = game.handle_obtain(
      item=drop.item,
      target=game.hero,
      on_start=lambda: obtained and game.stage.remove_elem(drop),
    )

    if obtained:
      drop.obtained = True

    return obtained

  def view(drop, anims):
    anim_group = [a for a in anims[0] if a.target is drop] if anims else []
    offset_x, offset_y = (0, 0)
    offset_layer = "tiles" if drop.obtained else "elems"
    for anim in anim_group:
      if type(anim) is ItemDrop.ThrownAnim:
        col, row = anim.offset
        offset_x += col * TILE_SIZE
        offset_y += row * TILE_SIZE + (1 - anim.pos) * -16
        offset_layer = "vfx"
    return super().view([Sprite(
      image=drop.item().render(),
      pos=(offset_x, offset_y),
      offset=-8,
      layer=offset_layer,
    )], anims)
