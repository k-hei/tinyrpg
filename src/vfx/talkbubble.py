from pygame.transform import flip
from vfx import Vfx
from anims import Anim
from sprite import Sprite
import assets
from config import TILE_SIZE

class TalkBubble(Vfx):
  def __init__(bubble, cell, elev=0, duration=None, flipped=False):
    x, y = cell
    super().__init__(kind=None, pos=(x * TILE_SIZE, (y - elev) * TILE_SIZE))
    bubble.anim = duration and Anim(duration=duration) or None
    bubble.shown = True
    bubble.flipped = flipped

  def show(bubble):
    bubble.shown = True

  def hide(bubble):
    bubble.shown = False

  def update(bubble, _):
    if bubble.anim:
      if bubble.anim.done:
        bubble.anim = None
        bubble.done = True
      else:
        bubble.anim.update()

  def view(bubble):
    if not bubble.shown:
      return []
    bubble_image = assets.sprites["bubble_talk"]
    bubble_x, bubble_y = bubble.pos
    if bubble.flipped:
      bubble_x += TILE_SIZE - 8
      bubble_y += 28
      bubble_origin = Sprite.ORIGIN_TOPLEFT
      bubble_image = flip(bubble_image, False, True)
    else:
      bubble_x += TILE_SIZE - 8
      bubble_y += 8
      bubble_origin = Sprite.ORIGIN_BOTTOMLEFT

    return [Sprite(
      image=bubble_image,
      pos=(bubble_x, bubble_y),
      origin=bubble_origin,
      layer="vfx",
    )]
