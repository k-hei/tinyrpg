from math import sin, cos, pi
from pygame import Surface
from pygame.transform import scale
from assets import load as use_assets
from anims.tween import TweenAnim
from easing.expo import ease_out
from lib.lerp import lerp
from lib.sprite import Sprite
from colors.palette import BLACK, BLUE
from lib.filters import replace_color, darken_image

class EnterAnim(TweenAnim): pass
class ExitAnim(TweenAnim): pass
class WarpAnim(TweenAnim): pass
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
    card.exiting = False
    card.surface = None
    card.sprite = None

  def spin(card, duration=20, delay=0, on_end=None):
    card.anims.append(SpinAnim(duration=duration, delay=delay, on_end=on_end))

  def flip(card, duration=10, delay=0, on_end=None):
    def end():
      card.flipped = not card.flipped
      on_end and on_end()
    card.anims.append(FlipAnim(duration=duration, delay=delay, on_end=end))

  def enter(card, duration=12, delay=0, on_end=None):
    card.exiting = False
    card.anims.append(EnterAnim(duration=duration, delay=delay, on_end=on_end))

  def exit(card, duration=10, delay=0, on_end=None):
    card.exiting = True
    card.anims.append(ExitAnim(duration=duration, delay=delay, on_end=on_end))

  def warp(card, duration=8, delay=0, on_end=None):
    card.exiting = True
    card.anims.append(WarpAnim(duration=duration, delay=delay, on_end=on_end))

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
    if card_anim:
      t = card_anim.pos
      if type(card_anim) is SpinAnim:
        w = cos(t * 2 * pi)
      if type(card_anim) is FlipAnim:
        w = cos(t * pi)
      if type(card_anim) is SpinAnim or type(card_anim) is FlipAnim and not card_anim.done:
        if w < 0:
          card_image = card_front_image if card.flipped else card_back_image
        card_width *= abs(w)
      if type(card_anim) is EnterAnim:
        card_height *= ease_out(t)
      if type(card_anim) is ExitAnim:
        if t < 0.5:
          t /= 0.5
          card_height = lerp(card_height, 4, t)
        else:
          t = (t - 0.5) * 2
          card_width *= 1 - t
          card_height = 4
      if type(card_anim) is WarpAnim:
        card_width *= lerp(1, 0, t)
        card_height *= lerp(1, 2, t)
    if not card_anim and card.exiting:
      return None
    card_image = replace_color(card_image, BLACK, card.color)
    card.sprite = Sprite(
      image=card_image,
      pos=(0, card_y),
      size=(card_width, card_height),
      origin=("center", "center"),
      layer="card",
    )
    return card.sprite
