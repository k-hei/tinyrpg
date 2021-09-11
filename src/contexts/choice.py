from dataclasses import dataclass
from types import FunctionType as function
import pygame
from pygame import Surface, Rect

from assets import load as use_assets
from text import render as render_text
from contexts import Context
import lib.gamepad as gamepad
import keyboard
from filters import recolor, replace_color
from colors.palette import BLACK, WHITE, GRAY, GOLD

from anims.tween import TweenAnim
from anims.sine import SineAnim
from anims.flicker import FlickerAnim
from easing.expo import ease_out
from lib.lerp import lerp

BORDER_WIDTH = 5
PADDING = 8
PADDING_RIGHT = 16
CURSOR_PADDING = 6
CHOICE_SPACING = 6
ENTER_DURATION = 8
EXIT_DURATION = 6

@dataclass
class Choice:
  text: str
  default: bool = False
  closing: bool = False
  disabled: function = None

  def is_disabled(choice):
    return choice and choice.disabled and choice.disabled()

class ChoiceContext(Context):
  def __init__(ctx, choices, required=False, on_choose=None, on_close=None):
    super().__init__(on_close=on_close)
    ctx.choices_template = choices if callable(choices) else lambda: choices
    ctx.choices = ctx.choices_template()
    ctx.required = required
    ctx.on_choose = on_choose
    ctx.index = next((i for i, c in enumerate(ctx.choices) if c.default), 0)
    ctx.cursor = (BORDER_WIDTH + PADDING, SineAnim(30))
    ctx.choice = None
    ctx.exiting = False
    ctx.draws = 0
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

  def close(ctx):
    ctx.parent.child = None
    if ctx.on_close:
      ctx.on_close(ctx.choice)

  def handle_press(ctx, button):
    if ctx.anims or ctx.choice:
      return False

    if keyboard.get_pressed(button) > 1:
      return False

    if button in (pygame.K_UP, pygame.K_w, gamepad.UP):
      return ctx.handle_move(-1)
    elif button in (pygame.K_DOWN, pygame.K_s, gamepad.DOWN):
      return ctx.handle_move(1)

    if button in (pygame.K_RETURN, pygame.K_SPACE, gamepad.controls.confirm):
      return ctx.handle_choose()

    if button in (pygame.K_BACKSPACE, pygame.K_ESCAPE, gamepad.controls.cancel):
      return ctx.handle_close()

  def handle_move(ctx, delta):
    old_index = ctx.index
    new_index = old_index + delta
    while (new_index >= 0
    and new_index < len(ctx.choices)
    and ctx.choices[new_index].is_disabled()):
      new_index += delta
    if new_index >= 0 and new_index < len(ctx.choices):
      ctx.index = new_index

  def choose(ctx):
    choice = ctx.choices[ctx.index]
    ctx.choice = choice
    if choice.closing:
      ctx.exit()
    else:
      ctx.anims.append(FlickerAnim(
        duration=45,
        target="cursor",
        on_end=ctx.exit
      ))

  def handle_choose(ctx):
    choice = ctx.choices[ctx.index]
    chosen = ctx.on_choose and ctx.on_choose(choice)
    ctx.choices = ctx.choices_template()
    if not ctx.on_choose or chosen:
      ctx.choose()

  def handle_close(ctx):
    if ctx.required:
      return False
    ctx.exit()
    return True

  def render(ctx):
    assets = use_assets()
    font = assets.ttf["normal"]
    cursor = replace_color(assets.sprites["cursor"], WHITE, GOLD)

    choice_widths = map(lambda c: font.width(c.text), ctx.choices)
    INNER_WIDTH = max(*choice_widths)
    INNER_HEIGHT = max(0, len(ctx.choices) * (font.height() + CHOICE_SPACING) - CHOICE_SPACING)
    box_width = BORDER_WIDTH + PADDING + cursor.get_width() + CURSOR_PADDING + INNER_WIDTH + PADDING_RIGHT + BORDER_WIDTH
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
          color = GOLD
        if choice.is_disabled():
          color = GRAY
        text = font.render(choice.text, color)
        if visible:
          surface.blit(text, (x, y))
        y += text.get_height() + CHOICE_SPACING

      # draw cursor
      if not cursor_anim or cursor_anim.visible:
        x = BORDER_WIDTH + PADDING
        y, anim = ctx.cursor
        target_y = BORDER_WIDTH + PADDING + ctx.index * (CHOICE_SPACING + font.height() + 0.25) + 1
        if not cursor_anim:
          x += anim.update() * 1.0625
        if anim.time == 1:
          y = target_y
        else:
          y += (target_y - y) / 2
        ctx.cursor = (y, anim)
        surface.blit(cursor, (x, y))

    ctx.draws += 1
    return surface
