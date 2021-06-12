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

CARD_BUY = "buy"
CARD_SELL = "sell"
CARD_EXIT = "exit"

class Card:
  def __init__(card, name, flipped=False, color=BLUE):
    card.name = name
    card.flipped = flipped
    card.color = color
    card.anims = []
    card.surface = None
    card.sprite = None

  def spin(card, duration=20, delay=0, on_end=None):
    card.anims.append(SpinAnim(
      duration=duration,
      delay=delay,
      on_end=on_end
    ))

  def flip(card, duration=10, delay=0, on_end=None):
    def end():
      card.flipped = not card.flipped
      on_end and on_end()
    card.anims.append(FlipAnim(
      duration=duration,
      delay=delay,
      on_end=end
    ))

  def update(card):
    for anim in card.anims:
      if anim.done:
        card.anims.remove(anim)
      else:
        anim.update()

  def render(card):
    card.update()
    sprites = use_assets().sprites
    card_front_image = sprites["card_" + card.name]
    card_back_image = sprites["card_back"]
    card_image = card_back_image if card.flipped else card_front_image
    card_width, card_height = card_image.get_size()
    card_anim = card.anims and card.anims[0]
    card_y = 0
    if card_anim and not card_anim.done:
      t = card_anim.pos
      if type(card_anim) is SpinAnim:
        w = cos(t * 2 * pi)
      elif type(card_anim) is FlipAnim:
        w = cos(t * pi)
      if type(card_anim) is SpinAnim or type(card_anim) is FlipAnim:
        if w < 0:
          card_image = card_front_image if card.flipped else card_back_image
        card_width *= abs(w)

    card_image = replace_color(card_image, BLACK, card.color)
    card.sprite = Sprite(
      image=card_image,
      pos=(0, card_y),
      size=(card_width, card_height),
      origin=("center", "center")
    )
    return card.sprite
