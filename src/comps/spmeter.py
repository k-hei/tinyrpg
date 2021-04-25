import math
from pygame import Rect
from assets import load as use_assets

MARGIN = 12
PADDING_X = 3
PADDING_Y = 4
TAG_X = 18
TAG_Y = 28

class SpMeter:
  def __init__(meter):
    pass

  def draw(meter, surface, ctx):
    assets = use_assets()
    sp_pct = min(1, ctx.sp / ctx.sp_max)
    meter_sprite = assets.sprites["sp_meter"]
    fill_sprite = assets.sprites["sp_fill"]
    tag_sprite = assets.sprites["sp_tag"]
    if sp_pct < 1:
      y = fill_sprite.get_height() * (1 - sp_pct)
      fill_sprite = fill_sprite.subsurface(Rect(
        (0, math.ceil(y)),
        (fill_sprite.get_width(), fill_sprite.get_height() - y)
      ))

    meter_x = surface.get_width() - meter_sprite.get_width() - MARGIN
    meter_y = surface.get_height() - meter_sprite.get_height() - MARGIN

    x, y = meter_x, meter_y
    surface.blit(meter_sprite, (x, y))

    x += PADDING_X
    y += meter_sprite.get_height() - PADDING_Y - fill_sprite.get_height()
    surface.blit(fill_sprite, (x, y))

    x = meter_x + TAG_X
    y = meter_y + TAG_Y
    surface.blit(tag_sprite, (x, y))
