from pygame import Rect
from comps import Component
import assets
from sprite import Sprite
from filters import replace_color
from colors.palette import WHITE, RED

class HpBubble(Component):
  def __init__(bubble, actor):
    bubble.actor = actor
    bubble.hp = actor.get_hp()

  def view(bubble):
    bubble.hp = bubble.actor.get_hp()
    if bubble.hp == bubble.actor.get_hp_max():
      return []
    sprites = [Sprite(
      image=replace_color(assets.sprites["hpbubble"], WHITE, RED),
      layer="vfx"
    )]
    if bubble.hp:
      fill_image = assets.sprites["hpbubble_fill"]
      fill_height = bubble.hp / bubble.actor.get_hp_max() * fill_image.get_height()
      fill_image = fill_image.subsurface(Rect(
        (0, fill_image.get_height() - fill_height),
        (fill_image.get_width(), fill_height)
      ))
      sprites.append(Sprite(
        image=fill_image,
        pos=(1, -5),
        offset=32,
        layer="vfx"
      ))
    return sprites
