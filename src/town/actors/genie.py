from math import pi, sin
from pygame import Surface, Rect
from easing.expo import ease_out
from assets import load as use_assets
from cores import Core
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
  def __init__(genie, name=None, message=None):
    super().__init__(Core(name, faction="ally"), message)
    genie.renders = 0

  def render(genie):
    sprite_genie = use_assets().sprites["genie"]
    sprite = Surface((32, 32)).convert_alpha()
    sprite.blit(sprite_genie.subsurface(Rect(0, 0, 32, RIPPLE_START)), (0, 0))
    for y in range(RIPPLE_START, RIPPLE_END):
      i = y - RIPPLE_START
      p = i / RIPPLE_EXTENT
      t = genie.renders
      t = t + p * RIPPLE_PERIOD
      t = (t % (RIPPLE_PERIOD / RIPPLE_WAVES) / RIPPLE_PERIOD) * RIPPLE_WAVES
      x = sin(t * 2 * pi) * ease_out(p) * RIPPLE_AMP
      sprite.blit(sprite_genie.subsurface(Rect(0, y, 32, 1)), (x, y))
    sprite, _, _ = super().render(sprite)
    x = 0
    y = sin(genie.renders % FLOAT_PERIOD / FLOAT_PERIOD * 2 * pi) * FLOAT_AMP
    genie.renders += 1
    return (sprite, x, y)
