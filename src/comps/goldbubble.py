from pygame import Surface, SRCALPHA
import assets
from colors.palette import GRAY

VALUE_X = 19
VALUE_Y = 9
DIGITS = 4

class GoldBubble:
  def __init__(bubble, gold=0):
    bubble.gold = gold

  @property
  def gold(bubble):
    return bubble._gold

  @gold.setter
  def gold(bubble, gold):
    bubble._gold = gold

  def render(bubble):
    bubble_surface = assets.sprites["bubble_gold"].copy()
    prefix_image = assets.ttf["english"].render("0" * (DIGITS - len(str(bubble.gold))), GRAY)
    value_image = assets.ttf["english"].render(str(bubble.gold))
    value_surface = Surface((prefix_image.get_width() + value_image.get_width(), prefix_image.get_height()), flags=SRCALPHA)
    value_surface.blit(prefix_image, (0, 0))
    value_surface.blit(value_image, (prefix_image.get_width(), 0))
    bubble_surface.blit(value_surface, (VALUE_X, VALUE_Y))
    return bubble_surface
