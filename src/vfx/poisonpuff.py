from vfx import Vfx
import assets
from sprite import Sprite
from anims.offsetmove import OffsetMoveAnim
from config import TILE_SIZE

class PoisonPuff(Vfx):
  def __init__(puff, src, dest):
    x, y = src
    super().__init__(kind=None, pos=(x * TILE_SIZE, y * TILE_SIZE))
    puff.anim = OffsetMoveAnim(src, dest)

  def update(bubble, *_):
    if bubble.anim.done:
      bubble.done = True
    else:
      bubble.anim.update()

  def view(bubble):
    bubble_image = assets.sprites["bubble_alert"]
    bubble_x, bubble_y = bubble.pos
    bubble_x += TILE_SIZE - 8
    bubble_y -= 12
    return [Sprite(
      image=bubble_image,
      pos=(bubble_x, bubble_y),
      layer="vfx",
    )]
