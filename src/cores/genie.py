from math import pi, sin
from pygame import Surface, Rect, SRCALPHA
from easing.expo import ease_out
from assets import load as use_assets
from cores import Core
from sprite import Sprite
from filters import replace_color
from colors.palette import BLACK, ORANGE
from colorsys import hsv_to_rgb

RIPPLE_PERIOD = 90
RIPPLE_WAVES = 2
RIPPLE_START = 20
RIPPLE_END = 32
RIPPLE_EXTENT = RIPPLE_END - RIPPLE_START
RIPPLE_AMP = 4
FLOAT_PERIOD = 180
FLOAT_AMP = 2

class Genie(Core):
  def __init__(genie, name, faction="ally", *args, **kwargs):
    super().__init__(name=name, faction=faction, *args, **kwargs)
    genie.renders = 0

  def view(genie):
    genie_image = use_assets().sprites["genie"]
    genie_surface = Surface(genie_image.get_size(), SRCALPHA).convert_alpha()
    genie_surface.blit(genie_image.subsurface(Rect(0, 0, 32, RIPPLE_START)), (0, 0))
    for y in range(RIPPLE_START, RIPPLE_END):
      i = y - RIPPLE_START
      p = i / RIPPLE_EXTENT
      t = genie.renders
      t = t + p * RIPPLE_PERIOD
      t = (t % (RIPPLE_PERIOD / RIPPLE_WAVES) / RIPPLE_PERIOD) * RIPPLE_WAVES
      x = sin(t * 2 * pi) * ease_out(p) * RIPPLE_AMP
      genie_surface.blit(genie_image.subsurface(Rect(0, y, 32, 1)), (x, y))
    y = sin(genie.renders % FLOAT_PERIOD / FLOAT_PERIOD * 2 * pi) * FLOAT_AMP
    # hue = genie.renders % 180 / 180
    # color = tuple([int(c * 255) for c in hsv_to_rgb(hue, 1, 1)])
    genie_surface = replace_color(genie_surface, BLACK, genie.color or ORANGE)
    genie.renders += 1
    return [Sprite(
      image=genie_surface,
      pos=(0, y),
      flip=(genie.facing == (-1, 0), False),
      layer="elems"
    )]
