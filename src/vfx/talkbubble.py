from pygame.transform import flip
from vfx import Vfx
from anims.frame import FrameAnim
from lib.sprite import Sprite
from lib.filters import replace_color
import assets
from colors.palette import BLACK, BLUE
from config import TILE_SIZE

class TalkBubble(Vfx):
  class Anim(FrameAnim):
    frames = [replace_color(s, BLACK, BLUE) for s in assets.sprites["bubble_talk"]]
    frames_duration = 10
    loop = True

  def __init__(bubble, cell, elev=0, duration=None, target=None, flipped=False):
    x, y = cell
    super().__init__(kind=None, pos=(x * TILE_SIZE, (y - elev) * TILE_SIZE))
    bubble.anim = TalkBubble.Anim(duration=duration)
    bubble.target = target
    bubble.flipped = flipped
    bubble.shown = True

  def show(bubble):
    bubble.shown = True

  def hide(bubble):
    bubble.shown = False

  def update(bubble, *_):
    if bubble.anim:
      if bubble.anim.done:
        bubble.anim = None
        bubble.done = True
      else:
        bubble.anim.update()

  def view(bubble):
    if not bubble.shown:
      return []

    bubble_image = bubble.anim.frame()
    bubble_x, bubble_y = bubble.pos
    bubble_x += TILE_SIZE - 4
    if bubble.flipped:
      bubble_y += 28
      bubble_origin = Sprite.ORIGIN_TOPLEFT
      bubble_image = flip(bubble_image, False, True)
    else:
      bubble_y += 8
      bubble_origin = Sprite.ORIGIN_BOTTOMLEFT

    return [Sprite(
      image=bubble_image,
      pos=(bubble_x, bubble_y),
      origin=bubble_origin,
      layer="vfx",
    )]
