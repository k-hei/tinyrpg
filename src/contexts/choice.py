import pygame
from pygame import Surface, Rect

from assets import load as use_assets
from text import render as render_text
from contexts import Context
from keyboard import key_times
from filters import recolor
import palette

from anims.tween import TweenAnim
from easing.expo import ease_out
from lerp import lerp

BORDER_WIDTH = 5
PADDING_LEFT = BORDER_WIDTH + 16
PADDING_TOP = BORDER_WIDTH + 8
PADDING_RIGHT = BORDER_WIDTH + 8
PADDING_BOTTOM = BORDER_WIDTH + 8
SPACING = 6
ENTER_DURATION = 8
EXIT_DURATION = 6

class ChoiceContext(Context):
  def __init__(ctx, parent, choices, on_choose, on_close=None):
    ctx.index = 0
    ctx.parent = parent
    ctx.choices = choices
    ctx.chosen = False
    ctx.exiting = False
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

    if key == pygame.K_UP:
      ctx.handle_move(-1)
    elif key == pygame.K_DOWN:
      ctx.handle_move(1)

    if key not in key_times or key_times[key] != 1:
      return False

    if key == pygame.K_RETURN:
      ctx.handle_choose()

    if key == pygame.K_BACKSPACE:
      ctx.handle_close()

  def handle_move(ctx, delta):
    old_index = ctx.index
    new_index = old_index + delta
    if new_index >= 0 and new_index < len(ctx.choices):
      ctx.index = new_index

  def handle_choose(ctx):
    choice = ctx.choices[ctx.index]
    ctx.chosen = True
    ctx.on_choose(choice)
    ctx.exit()

  def handle_close(ctx):
    ctx.exit()

  def close(ctx):
    ctx.parent.child = None
    if ctx.on_close: ctx.on_close()

  def render(ctx):
    assets = use_assets()
    font = assets.fonts["smallcaps"]

    INNER_WIDTH = max(*map(lambda c: len(c), ctx.choices)) * (font.char_width + font.char_spacing)
    INNER_HEIGHT = max(0, len(ctx.choices) * (font.char_height + SPACING) - SPACING)
    box_width = PADDING_LEFT + INNER_WIDTH + PADDING_RIGHT
    box_height = PADDING_TOP + INNER_HEIGHT + PADDING_BOTTOM

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


    if not ctx.anims:
      x = PADDING_LEFT
      y = PADDING_TOP
      for choice in ctx.choices:
        color = palette.WHITE
        if choice == ctx.choices[ctx.index]:
          color = palette.YELLOW
        text = recolor(render_text(choice.upper(), font), color)
        surface.blit(text, (x, y))
        y += text.get_height() + SPACING
    return surface
