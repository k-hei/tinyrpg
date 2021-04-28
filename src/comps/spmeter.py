import math
from pygame import Surface, Rect
from assets import load as use_assets
from anims.tween import TweenAnim
from easing.expo import ease_out
from lerp import lerp
from comps.hud import render_numbers
from filters import recolor
import palette

MARGIN = 12
PADDING_X = 3
PADDING_Y = 4
TAG_X = 16
TAG_Y = 28
ENTER_DURATION = 8
EXIT_DURATION = 6
NUMBERS_OVERLAP = 20
NUMBERS_OFFSET = -2
SPEED_DEPLETE = 1 / 500
SPEED_RESTORE = 1 / 500

class SpMeter:
  def __init__(meter):
    meter.active = False
    meter.sp_drawn = 1
    meter.draws = 0
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
    meter_sprite = assets.sprites["sp_meter"]
    tag_sprite = assets.sprites["sp_tag"]
    fill_sprite = assets.sprites["sp_fill"]
    fill_y = 0
    sp_pct = min(1, ctx.sp / ctx.sp_max)
    if sp_pct > meter.sp_drawn:
      meter.sp_drawn += min(sp_pct - meter.sp_drawn, SPEED_RESTORE)
    elif sp_pct < meter.sp_drawn:
      delta = max(sp_pct - meter.sp_drawn, -SPEED_DEPLETE)
      meter.sp_drawn += delta
      if meter.draws % 2 and delta == -SPEED_DEPLETE:
        fill_sprite = recolor(fill_sprite, palette.WHITE)
    if sp_pct < 1:
      fill_y = fill_sprite.get_height() * (1 - meter.sp_drawn)
      fill_sprite = fill_sprite.subsurface(Rect(
        (0, math.ceil(fill_y)),
        (fill_sprite.get_width(), fill_sprite.get_height() - math.ceil(fill_y))
      ))

    numbers_sprite = render_numbers(ctx.sp, ctx.sp_max)
    numbers_x = 0
    numbers_y = meter_sprite.get_height() // 2 - numbers_sprite.get_height() // 2 + NUMBERS_OFFSET
    sprite = Surface((
      meter_sprite.get_width() + numbers_sprite.get_width() - NUMBERS_OVERLAP,
      meter_sprite.get_height()
    )).convert_alpha()

    meter_x = numbers_sprite.get_width() - NUMBERS_OVERLAP
    meter_y = 0
    sprite.blit(meter_sprite, (meter_x, meter_y))
    sprite.blit(fill_sprite, (meter_x + PADDING_X, meter_y + PADDING_Y + math.ceil(fill_y)))
    sprite.blit(numbers_sprite, (numbers_x, numbers_y))
    sprite.blit(tag_sprite, (
      meter_x + meter_sprite.get_width() - tag_sprite.get_width(),
      meter_y + meter_sprite.get_height() - tag_sprite.get_height()
    ))

    meter.draws += 1
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
