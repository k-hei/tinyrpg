from math import pi, sin
from cores import Core
import assets
from sprite import Sprite
from lib.filters import ripple, replace_color
from colors.palette import BLACK, ORANGE

FLOAT_PERIOD = 180
FLOAT_AMP = 2

class Genie(Core):
  def __init__(genie, name, faction="ally", *args, **kwargs):
    super().__init__(name=name, faction=faction, *args, **kwargs)
    genie.renders = 0

  def view(genie):
    genie_image = assets.sprites["genie"]
    genie_image = ripple(genie_image, start=20, end=32, time=genie.renders)
    genie_image = replace_color(genie_image, BLACK, genie.color or ORANGE)
    genie_y = sin(genie.renders % FLOAT_PERIOD / FLOAT_PERIOD * 2 * pi) * FLOAT_AMP
    genie.renders += 1
    return [Sprite(
      image=genie_image,
      pos=(0, genie_y),
      flip=(genie.facing == (-1, 0), False),
      layer="elems"
    )]
