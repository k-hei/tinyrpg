import math
from assets import load as use_assets
from actors.town import Actor
from pygame import Surface, Rect

RIPPLE_PERIOD = 120
RIPPLE_START = 20
RIPPLE_END = 32
RIPPLE_EXTENT = RIPPLE_END - RIPPLE_START
RIPPLE_AMP = 6

class Genie(Actor):

  def __init__(genie):
    super().__init__()
    genie.renders = 0

  def render(genie):
    sprite_genie = use_assets().sprites["genie"]
    sprite = Surface((32, 32)).convert_alpha()
    sprite.blit(sprite_genie.subsurface(Rect(0, 0, 32, RIPPLE_START)), (0, 0))
    for y in range(RIPPLE_START, RIPPLE_END):
      i = y - RIPPLE_START
      t = genie.renders + i / RIPPLE_EXTENT * RIPPLE_PERIOD
      t = t % RIPPLE_PERIOD / RIPPLE_PERIOD
      x = math.sin(2 * math.pi * t) * i / RIPPLE_EXTENT * RIPPLE_AMP
      sprite.blit(sprite_genie.subsurface(Rect(0, y, 32, 1)), (x, y))
    genie.renders += 1
    return super().render(sprite)
