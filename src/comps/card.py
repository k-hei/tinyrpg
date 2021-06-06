from math import sin, cos, pi
from pygame import Surface
from pygame.transform import scale
from assets import load as use_assets
from anims.tween import TweenAnim
from easing.expo import ease_out
from sprite import Sprite
from palette import BLACK, BLUE
from filters import replace_color, darken

class SpinAnim(TweenAnim): pass
class FlipAnim(TweenAnim): pass

class Card:
  def __init__(card, name, color=BLUE):
    card.name = name
    card.color = color
    card.anims = []
    card.surface = None

  def spin(card, on_end=None):
    card.anims.append(SpinAnim(duration=20, on_end=on_end))

  def update(card):
    for anim in card.anims:
      if anim.done:
        card.anims.remove(anim)
      else:
        anim.update()

  def render(card):
    card.update()
    sprites = use_assets().sprites
    card_image = sprites["card_" + card.name]
    card_width, card_height = card_image.get_size()
    card_anim = card.anims and card.anims[0]
    card_y = 0
    if card_anim:
      t = card_anim.pos
      if type(card_anim) is SpinAnim:
        w = cos(t * 2 * pi)
        if w < 0:
          card_image = sprites["card_back"]
        card_width *= abs(w)
      elif type(card_anim) is FlipAnim:
        w = cos(t * pi)
        if w < 0:
          card_image = sprites["card_back"]
        card_width *= abs(w)
    card_image = replace_color(card_image, BLACK, card.color)
    return Sprite(
      image=card_image,
      pos=(0, card_y),
      size=(card_width, card_height),
      origin=("center", "center")
    )
