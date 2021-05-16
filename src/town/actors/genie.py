from math import pi, sin
from pygame import Surface, Rect
from easing.expo import ease_out
from assets import load as use_assets
from cores.genie import Genie as GenieCore
from town.actors.npc import Npc

RIPPLE_PERIOD = 90
RIPPLE_WAVES = 2
RIPPLE_START = 20
RIPPLE_END = 32
RIPPLE_EXTENT = RIPPLE_END - RIPPLE_START
RIPPLE_AMP = 4
FLOAT_PERIOD = 180
FLOAT_AMP = 2

class Genie(Npc):
  def __init__(genie, name=None, messages=None):
    super().__init__(GenieCore(name), messages)

  def render(genie):
    genie.sprite = genie.core.render()
    return super().render()
