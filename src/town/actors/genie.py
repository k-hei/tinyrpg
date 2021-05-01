from math import pi, sin
from assets import load as use_assets
from cores import Core
from town.actors.npc import Npc
from pygame import Surface, Rect

RIPPLE_PERIOD = 120
RIPPLE_START = 20
RIPPLE_END = 32
RIPPLE_EXTENT = RIPPLE_END - RIPPLE_START
RIPPLE_AMP = 6
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
      t = genie.renders + i / RIPPLE_EXTENT * RIPPLE_PERIOD
      t = t % RIPPLE_PERIOD / RIPPLE_PERIOD
      x = sin(t * 2 * pi) * i / RIPPLE_EXTENT * RIPPLE_AMP
      sprite.blit(sprite_genie.subsurface(Rect(0, y, 32, 1)), (x, y))
    sprite, _, _ = super().render(sprite)
    x = 0
    y = sin(genie.renders % FLOAT_PERIOD / FLOAT_PERIOD * 2 * pi) * FLOAT_AMP
    genie.renders += 1
    return (sprite, x, y)
