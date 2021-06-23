from assets import load as use_assets
from anims.tween import TweenAnim
from easing.expo import ease_out
from lib.lerp import lerp
from text import render as render_text
from filters import recolor, replace_color
from palette import BLACK
from sprite import Sprite
from config import WINDOW_WIDTH, WINDOW_HEIGHT

MARGIN_X = 12
MARGIN_Y = 6
TEXT_X = 36
TEXT_Y = 6
ENTER_DURATION = 15
EXIT_DURATION = 7

class FloorNo:
  def __init__(ctx, parent):
    ctx.parent = parent
    ctx.active = False
    ctx.anim = None
    ctx.enter()

  def enter(ctx):
    ctx.active = True
    ctx.anim = TweenAnim(duration=ENTER_DURATION)

  def exit(ctx):
    ctx.active = False
    ctx.anim = TweenAnim(duration=EXIT_DURATION)

  def render(ctx, game):
    assets = use_assets()
    image = assets.sprites["floorno"].copy()
    floor_no = game.get_floor_no()
    text = render_text(str(floor_no), assets.fonts["floornos"])
    image.blit(text, (TEXT_X, TEXT_Y))
    return image

  def view(ctx):
    game = ctx.parent
    image = ctx.render(game)
    hidden_x = WINDOW_WIDTH
    hidden_y = WINDOW_HEIGHT - image.get_height() - MARGIN_Y
    corner_x = hidden_x - image.get_width() - MARGIN_X
    corner_y = hidden_y
    anim = ctx.anim
    if anim:
      t = anim.update()
      if ctx.active:
        t = ease_out(t)
        start_x, start_y = hidden_x, hidden_y
        target_x, target_y = corner_x, corner_y
      else:
        start_x, start_y = corner_x, corner_y
        target_x, target_y = hidden_x, hidden_y
      x = lerp(start_x, target_x, t)
      y = lerp(start_y, target_y, t)
      if anim.done:
        ctx.anim = None
    elif ctx.active:
      x = corner_x
      y = corner_y
    else:
      return
    return [Sprite(
      image=image,
      pos=(x, y)
    )]
