from math import ceil, sin, pi
from pygame import Surface, Rect
from assets import load as use_assets
from anims.tween import TweenAnim
from easing.expo import ease_out
from lib.lerp import lerp
from comps.hud import render_numbers
from filters import recolor, replace_color
from palette import RED, WHITE, BLUE

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
SPEED_RESTORE = 1 / 250

class SpMeter:
  def __init__(meter):
    meter.active = False
    meter.sp_drawn = None
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
    delta = 0
    sp_pct = min(1, ctx.sp / (ctx.sp_max or 1))
    if meter.sp_drawn == None:
      meter.sp_drawn = sp_pct
    elif sp_pct > meter.sp_drawn:
      delta = min(sp_pct - meter.sp_drawn, SPEED_RESTORE)
      meter.sp_drawn += delta
    elif sp_pct < meter.sp_drawn:
      delta = max(sp_pct - meter.sp_drawn, -SPEED_DEPLETE)
      meter.sp_drawn += delta

    if delta == -SPEED_DEPLETE and meter.draws % 2:
      fill_sprite = recolor(fill_sprite, WHITE)

    bg_sprite = None
    if delta > 0:
      alpha = sin(meter.draws % 30 / 30 * 2 * pi) * 0x7F + 0x7F
      bg_sprite = replace_color(fill_sprite, BLUE, (*WHITE, alpha))
      bg_y = bg_sprite.get_height() * (1 - sp_pct)
      bg_sprite = bg_sprite.subsurface(Rect(
        (0, ceil(bg_y)),
        (bg_sprite.get_width(), bg_sprite.get_height() - ceil(bg_y))
      ))

    if meter.sp_drawn < 1:
      fill_y = fill_sprite.get_height() * (1 - meter.sp_drawn)
      fill_sprite = fill_sprite.subsurface(Rect(
        (0, ceil(fill_y)),
        (fill_sprite.get_width(), fill_sprite.get_height() - ceil(fill_y))
      ))

    sp = meter.sp_drawn * ctx.sp_max
    if ceil(sp) == ctx.sp_max:
      sp = ctx.sp_max
    elif int(sp) == 0:
      sp = 0
    numbers_sprite = render_numbers(sp, ctx.sp_max)
    numbers_x = 0
    numbers_y = meter_sprite.get_height() // 2 - numbers_sprite.get_height() // 2 + NUMBERS_OFFSET

    if ctx.sp == 0:
      tag_sprite = replace_color(tag_sprite, BLUE, RED)

    sprite = Surface((
      meter_sprite.get_width() + numbers_sprite.get_width() - NUMBERS_OVERLAP,
      meter_sprite.get_height()
    )).convert_alpha()

    meter_x = numbers_sprite.get_width() - NUMBERS_OVERLAP
    meter_y = 0
    sprite.blit(meter_sprite, (meter_x, meter_y))
    if bg_sprite:
      sprite.blit(bg_sprite, (meter_x + PADDING_X, meter_y + PADDING_Y + ceil(bg_y)))
    sprite.blit(fill_sprite, (meter_x + PADDING_X, meter_y + PADDING_Y + ceil(fill_y)))
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
