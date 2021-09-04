from random import random
from lib.cell import add as add_vector
from dungeon.props import Prop
import assets
from sprite import Sprite
from anims.offsetmove import OffsetMoveAnim
from config import TILE_SIZE
from filters import replace_color
from colors.palette import WHITE, VIOLET

class PoisonPuff(Prop):
  def __init__(puff, origin, *args, **kwargs):
    super().__init__(*args, **kwargs)
    puff.anim = origin

  def effect(puff, game, actor=None):
    actor = actor or game.hero
    game.poison_actor(actor)

  def view(puff, anims):
    if type(puff.anim) is tuple:
      get_random_offset = lambda: (random() - 0.5) / 2
      src = puff.anim
      dest = add_vector(puff.cell, (get_random_offset(), get_random_offset()))
      puff.anim = OffsetMoveAnim(target=puff, src=puff.anim, dest=dest, speed=2)
      not anims and anims.append([])
      anims[0].append(puff.anim)
    puff_xoffset, puff_yoffset = (0, 0)
    anim_group = [a for a in anims[0] if a.target is puff] if anims else []
    for anim in anim_group:
      if type(anim) is OffsetMoveAnim:
        offset_x, offset_y = anim.offset
        normal_x, normal_y = anim.normal
        puff_xoffset += (offset_x - normal_x * anim.duration * anim.speed) * TILE_SIZE
        puff_yoffset += (offset_y - normal_y * anim.duration * anim.speed) * TILE_SIZE
    puff_image = assets.sprites["fx_poisonpuff"]
    puff_image = replace_color(puff_image, WHITE, VIOLET)
    return super().view([Sprite(
      image=puff_image,
      pos=(puff_xoffset, puff_yoffset)
    )], anims)
