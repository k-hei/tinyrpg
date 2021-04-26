import pygame
from pygame import Surface, Rect

from assets import load as use_assets
from text import render as render_text
from contexts import Context
from keyboard import key_times
from filters import recolor, replace_color
import palette

from anims.tween import TweenAnim
from anims.sine import SineAnim
from easing.expo import ease_out
from lerp import lerp

BORDER_WIDTH = 5
PADDING = 8
CURSOR_PADDING = 6
SPACING = 6
ENTER_DURATION = 8
EXIT_DURATION = 6

class ChoiceContext(Context):
  def __init__(ctx, parent, choices, on_choose, on_close=None):
    super().__init__(parent)
    ctx.choices = choices
    ctx.index = 0
    ctx.cursor = (BORDER_WIDTH + PADDING, SineAnim(30))
    ctx.chosen = False
    ctx.exiting = False
    ctx.time = 0
    ctx.on_choose = on_choose
    ctx.on_close = on_close
    ctx.anims = []
    ctx.enter()

  def enter(ctx):
    ctx.anims.append(TweenAnim(
      duration=ENTER_DURATION,
      target=ctx
    ))

  def exit(ctx):
    ctx.exiting = True
    ctx.anims.append(TweenAnim(
      duration=EXIT_DURATION,
      target=ctx,
      on_end=ctx.close
    ))

  def handle_keydown(ctx, key):
    if ctx.anims or ctx.chosen:
      return False

    if key == pygame.K_UP or key == pygame.K_w:
      ctx.handle_move(-1)
    elif key == pygame.K_DOWN or key == pygame.K_s:
      ctx.handle_move(1)

    if key not in key_times or key_times[key] != 1:
      return False

    if key == pygame.K_RETURN or key == pygame.K_SPACE:
      ctx.handle_choose()

    if key == pygame.K_BACKSPACE or key == pygame.K_ESCAPE:
      ctx.handle_close()

  def handle_move(ctx, delta):
    old_index = ctx.index
    new_index = old_index + delta
    if new_index >= 0 and new_index < len(ctx.choices):
      ctx.index = new_index

  def handle_choose(ctx):
    choice = ctx.choices[ctx.index]
    if ctx.on_choose(choice):
      ctx.chosen = True
      ctx.exit()

  def handle_close(ctx):
    ctx.exit()

  def close(ctx):
    ctx.parent.child = None
    if ctx.on_close: ctx.on_close()

  def render(ctx):
    assets = use_assets()
    font = assets.fonts["smallcaps"]
    cursor = replace_color(assets.sprites["cursor"], palette.WHITE, palette.YELLOW)

    INNER_WIDTH = max(*map(lambda c: len(c), ctx.choices)) * (font.char_width + font.char_spacing)
    INNER_HEIGHT = max(0, len(ctx.choices) * (font.char_height + SPACING) - SPACING)
    box_width = BORDER_WIDTH + PADDING + cursor.get_width() + CURSOR_PADDING + INNER_WIDTH + PADDING + BORDER_WIDTH
    box_height = BORDER_WIDTH + PADDING + INNER_HEIGHT + PADDING + BORDER_WIDTH

    t = 1
    for anim in ctx.anims:
      if anim.done:
        ctx.anims.remove(anim)
        continue
      if anim.target is ctx:
        t = anim.update()
        if ctx.exiting:
          t = 1 - t
        else:
          t = ease_out(t)
        break
    else:
      if ctx.exiting:
        t = 0

    box_width *= t
    box_height *= t

    surface = pygame.Surface((box_width, box_height))
    pygame.draw.rect(surface, 0x000000, Rect(0, 0, box_width, box_height))
    pygame.draw.rect(surface, 0xFFFFFF, Rect(1, 1, box_width - 2, box_height - 2))
    pygame.draw.rect(surface, 0x000000, Rect(4, 4, box_width - 8, box_height - 8))

    # only render text if not animating
    if not ctx.anims:
      # draw text
      x = BORDER_WIDTH + PADDING + cursor.get_width() + CURSOR_PADDING
      y = BORDER_WIDTH + PADDING
      for choice in ctx.choices:
        color = palette.WHITE
        if choice == ctx.choices[ctx.index]:
          color = palette.YELLOW
        text = recolor(render_text(choice.upper(), font), color)
        surface.blit(text, (x, y))
        y += text.get_height() + SPACING

      # draw cursor
      x = BORDER_WIDTH + PADDING
      y, anim = ctx.cursor
      target_y = BORDER_WIDTH + PADDING + ctx.index * (SPACING + font.char_height + 1)
      x += anim.update() * 1.0625
      y += (target_y - y) / 4
      ctx.cursor = (y, anim)
      surface.blit(cursor, (x, y))

    return surface
