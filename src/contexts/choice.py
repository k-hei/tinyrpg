import pygame
from pygame import Surface, Rect

from assets import load as use_assets
from text import render as render_text
from contexts import Context
from keyboard import key_times
from filters import recolor, replace_color
from palette import BLACK, WHITE, YELLOW

from anims.tween import TweenAnim
from anims.sine import SineAnim
from anims.flicker import FlickerAnim
from easing.expo import ease_out
from lib.lerp import lerp

BORDER_WIDTH = 5
PADDING = 8
CURSOR_PADDING = 6
SPACING = 6
ENTER_DURATION = 8
EXIT_DURATION = 6

class ChoiceContext(Context):
  def __init__(ctx, choices, on_close=None):
    super().__init__(on_close=on_close)
    ctx.choices = choices
    ctx.index = next((i for i, c in enumerate(choices) if c.default), 0)
    ctx.cursor = (BORDER_WIDTH + PADDING, SineAnim(30))
    ctx.chosen = False
    ctx.exiting = False
    ctx.time = 0
    ctx.anims = []

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

  def choose(ctx):
    ctx.chosen = True
    ctx.anims.append(FlickerAnim(
      duration=45,
      target="cursor",
      on_end=ctx.exit
    ))

  def handle_choose(ctx):
    choice = ctx.choices[ctx.index]
    choice.on_choose(ctx.choose)

  def handle_close(ctx):
    ctx.exit()

  def render(ctx):
    assets = use_assets()
    font = assets.fonts["smallcaps"]
    cursor = replace_color(assets.sprites["cursor"], WHITE, YELLOW)

    choice_lengths = map(lambda c: len(c.text), ctx.choices)
    INNER_WIDTH = max(*choice_lengths) * (font.char_width + font.char_spacing)
    INNER_HEIGHT = max(0, len(ctx.choices) * (font.char_height + SPACING) - SPACING)
    box_width = BORDER_WIDTH + PADDING + cursor.get_width() + CURSOR_PADDING + INNER_WIDTH + PADDING + BORDER_WIDTH
    box_height = BORDER_WIDTH + PADDING + INNER_HEIGHT + PADDING + BORDER_WIDTH

    t = 1
    for anim in ctx.anims:
      if anim.done:
        ctx.anims.remove(anim)
        continue
      anim.update()
      if anim.target is ctx:
        t = anim.pos
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
    pygame.draw.rect(surface, BLACK, Rect(0, 0, box_width, box_height))
    pygame.draw.rect(surface, WHITE, Rect(1, 1, box_width - 2, box_height - 2))
    pygame.draw.rect(surface, BLACK, Rect(4, 4, box_width - 8, box_height - 8))

    # only render text if not animating
    cursor_anim = next((a for a in ctx.anims if a.target == "cursor"), None)
    if not ctx.anims or cursor_anim:
      # draw text
      x = BORDER_WIDTH + PADDING + cursor.get_width() + CURSOR_PADDING
      y = BORDER_WIDTH + PADDING
      for choice in ctx.choices:
        visible = True
        color = WHITE
        if choice is ctx.choices[ctx.index]:
          color = YELLOW
          if cursor_anim and not cursor_anim.visible:
            visible = False
        text = recolor(render_text(choice.text.upper(), font), color)
        if visible:
          surface.blit(text, (x, y))
        y += text.get_height() + SPACING

      # draw cursor
      if not cursor_anim or cursor_anim.visible:
        x = BORDER_WIDTH + PADDING
        y, anim = ctx.cursor
        target_y = BORDER_WIDTH + PADDING + ctx.index * (SPACING + font.char_height + 1)
        if not cursor_anim:
          x += anim.update() * 1.0625
        y += (target_y - y) / 4
        ctx.cursor = (y, anim)
        surface.blit(cursor, (x, y))

    return surface
