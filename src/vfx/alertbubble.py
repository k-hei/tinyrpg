from vfx import Vfx
from anims import Anim
from lib.sprite import Sprite
from assets import load as use_assets
from config import TILE_SIZE

class AlertBubble(Vfx):
  def __init__(bubble, cell, duration=45):
    x, y = cell
    super().__init__(kind=None, pos=(x * TILE_SIZE, y * TILE_SIZE))
    bubble.anim = Anim(duration=duration)

  def update(bubble, _):
    if bubble.anim.done:
      bubble.done = True
    else:
      bubble.anim.update()

  def view(bubble):
    assets = use_assets().sprites
    bubble_image = assets["bubble_alert"]
    bubble_x, bubble_y = bubble.pos
    bubble_x += TILE_SIZE - 8
    bubble_y -= 12
    return [Sprite(
      image=bubble_image,
      pos=(bubble_x, bubble_y),
      layer="vfx",
    )]
