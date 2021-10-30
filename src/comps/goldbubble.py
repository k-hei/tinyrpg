from pygame import Surface, SRCALPHA
from lib.sprite import Sprite
import lib.vector as vector
import assets
from comps.box import Box
from colors.palette import WHITE, GRAY, RED, CYAN

VALUE_X = 19
VALUE_Y = 9
DIGITS = 4
DELTA_XPADDING = 6
DELTA_YPADDING = 4

def render_gold(gold, color=WHITE):
  bubble_surface = assets.sprites["bubble_gold"].copy()
  prefix_image = assets.ttf["english"].render("0" * (DIGITS - len(str(gold))), GRAY)
  value_image = assets.ttf["english"].render(str(gold), color)
  value_surface = Surface((prefix_image.get_width() + value_image.get_width(), prefix_image.get_height()), flags=SRCALPHA)
  value_surface.blit(prefix_image, (0, 0))
  value_surface.blit(value_image, (prefix_image.get_width(), 0))
  bubble_surface.blit(value_surface, (VALUE_X, VALUE_Y))
  return bubble_surface

def render_delta(delta):
  delta_color = (
    delta == 0 and WHITE
    or delta < 0 and RED
    or delta > 0 and CYAN
  )
  delta_symbol = "+" if delta >= 0 else ""
  delta_image = assets.ttf["english"].render(text=delta_symbol + str(delta), color=delta_color)
  bubble_surface = Box(
    sprite_prefix="box_delta",
    size=(delta_image.get_width() + DELTA_XPADDING * 2, 16)
  ).render()
  bubble_surface.blit(delta_image, (bubble_surface.get_width() - delta_image.get_width() - DELTA_XPADDING, DELTA_YPADDING))
  return bubble_surface

class GoldBubble:
  def __init__(bubble, gold=0):
    bubble.gold = gold
    bubble.delta = 0

  @property
  def gold(bubble):
    return bubble._gold

  @gold.setter
  def gold(bubble, gold):
    bubble._gold = gold

  def view(bubble):
    return [bubble_sprite := Sprite(
      image=render_gold(bubble.gold, color=RED if -bubble.delta > bubble.gold else WHITE),
      pos=(0, 0),
      origin=Sprite.ORIGIN_LEFT
    ), *([delta_sprite := Sprite(
      image=render_delta(bubble.delta),
      pos=vector.add(
        bubble_sprite.rect.bottomright,
        (0, 2)
      ),
      origin=Sprite.ORIGIN_RIGHT
    )] if bubble.delta else [])]
