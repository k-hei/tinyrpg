from math import pi, sin
from pygame import Surface, Rect
from easing.expo import ease_out
from assets import load as use_assets
from cores import Core
from sprite import Sprite
from filters import replace_color
from palette import BLACK, GOLD

RIPPLE_PERIOD = 90
RIPPLE_WAVES = 2
RIPPLE_START = 20
RIPPLE_END = 32
RIPPLE_EXTENT = RIPPLE_END - RIPPLE_START
RIPPLE_AMP = 4
FLOAT_PERIOD = 180
FLOAT_AMP = 2

class Genie(Core):
  def __init__(genie, name=None):
    super().__init__(name=name, faction="ally")
    genie.sprite = Sprite()
    genie.renders = 0

  def render(genie):
    sprite_genie = use_assets().sprites["genie"]
    image = Surface(sprite_genie.get_size()).convert_alpha()
    image.blit(sprite_genie.subsurface(Rect(0, 0, 32, RIPPLE_START)), (0, 0))
    for y in range(RIPPLE_START, RIPPLE_END):
      i = y - RIPPLE_START
      p = i / RIPPLE_EXTENT
      t = genie.renders
      t = t + p * RIPPLE_PERIOD
      t = (t % (RIPPLE_PERIOD / RIPPLE_WAVES) / RIPPLE_PERIOD) * RIPPLE_WAVES
      x = sin(t * 2 * pi) * ease_out(p) * RIPPLE_AMP
      image.blit(sprite_genie.subsurface(Rect(0, y, 32, 1)), (x, y))
    y = sin(genie.renders % FLOAT_PERIOD / FLOAT_PERIOD * 2 * pi) * FLOAT_AMP
    genie.sprite.image = replace_color(image, BLACK, GOLD)
    genie.sprite.pos = (0, y)
    genie.renders += 1
    return genie.sprite
