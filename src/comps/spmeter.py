import math
from pygame import Rect
from assets import load as use_assets
from anims.tween import TweenAnim
from easing.expo import ease_out
from lerp import lerp

MARGIN = 12
PADDING_X = 3
PADDING_Y = 4
TAG_X = 18
TAG_Y = 28
ENTER_DURATION = 8
EXIT_DURATION = 6

class SpMeter:
  def __init__(meter):
    meter.active = False
    meter.anims = []
    meter.enter()

  def enter(meter):
    meter.active = True
    meter.anims.append(TweenAnim(duration=ENTER_DURATION))

  def exit(meter):
    meter.active = False
    meter.anims.append(TweenAnim(duration=EXIT_DURATION))

  def render(meter, ctx):
    assets = use_assets()
    sp_pct = min(1, ctx.sp / ctx.sp_max)
    sprite = assets.sprites["sp_meter"].copy()
    tag_sprite = assets.sprites["sp_tag"]
    fill_sprite = assets.sprites["sp_fill"]
    fill_y = 0
    if sp_pct < 1:
      fill_y = fill_sprite.get_height() * (1 - sp_pct)
      fill_sprite = fill_sprite.subsurface(Rect(
        (0, math.ceil(fill_y)),
        (fill_sprite.get_width(), fill_sprite.get_height() - fill_y)
      ))

    sprite.blit(fill_sprite, (PADDING_X, PADDING_Y + math.ceil(fill_y)))
    sprite.blit(tag_sprite, (TAG_X, TAG_Y))
    return sprite

  def draw(meter, surface, ctx):
    sprite = meter.render(ctx)
    hidden_x = surface.get_width()
    hidden_y = surface.get_height() - sprite.get_height() - MARGIN
    corner_x = hidden_x - sprite.get_width() - MARGIN
    corner_y = hidden_y
    anim = meter.anims[0] if meter.anims else None
    if anim:
      t = anim.update()
      if meter.active:
        t = ease_out(t)
        start_x, start_y = hidden_x, hidden_y
        target_x, target_y = corner_x, corner_y
      else:
        start_x, start_y = corner_x, corner_y
        target_x, target_y = hidden_x, hidden_y
      x = lerp(start_x, target_x, t)
      y = lerp(start_y, target_y, t)
      if anim.done:
        meter.anims.pop(0)
    elif meter.active:
      x = corner_x
      y = corner_y
    else:
      return
    surface.blit(sprite, (x, y))
