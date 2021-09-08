from vfx import Vfx
from anims import Anim
from sprite import Sprite
import assets
from config import TILE_SIZE

class TalkBubble(Vfx):
  def __init__(bubble, cell, elev=0, duration=None):
    x, y = cell
    super().__init__(kind=None, pos=(x * TILE_SIZE, (y - elev) * TILE_SIZE))
    bubble.anim = duration and Anim(duration=duration) or None
    bubble.shown = True

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
    bubble_x += TILE_SIZE - 8
    bubble_y -= 12
    return [Sprite(
      image=bubble_image,
      pos=(bubble_x, bubble_y),
      layer="vfx",
    )]
