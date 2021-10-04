from copy import copy
import pygame
from pygame import Surface, SRCALPHA
from pygame.transform import flip
from pygame.time import get_ticks
import lib.keyboard as keyboard
import lib.gamepad as gamepad
from lib.lerp import lerp

from contexts import Context
from contexts.prompt import PromptContext, Choice
import assets
from game.controls import TYPE_A
from comps.control import Control
from comps.title import Title
from comps.bg import Bg
from lib.sprite import Sprite
from anims import Anim
from anims.tween import TweenAnim
from anims.sine import SineAnim
from lib.filters import replace_color, darken_image
from config import WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_SIZE
from colors.palette import BLACK, WHITE, GRAY, BLUE, GOLD, GREEN

controls = [*{
  "LEFT": "Left",
  "RIGHT": "Right",
  "UP": "Up",
  "DOWN": "Down",
  "A": "A",
  "B": "B",
  "X": "X",
  "Y": "Y",
  "L": "L",
  "R": "R",
  "SELECT": "Select",
  "START": "Start",
  "confirm": "Confirm/Action",
  "cancel": "Cancel",
  "manage": "Manage",
  "run": "Run",
  "turn": "Turn",
  "wait": "Wait",
  "item": "Carry/Throw",
  "shortcut": "Skill shortcut",
  "skill": "Use skill",
  "ally": "Switch hero",
  "inventory": "Open inventory",
  "equip": "Change equipment",
  "minimap": "View minimap"
}.items()]
hold_controls = ["run", "turn"]

font = assets.ttf["normal"]
LINE_SPACING = 8
LINE_HEIGHT = font.height() + LINE_SPACING
CURSOR_OFFSET = -4
CURSOR_BOUNCE_AMP = 2
CURSOR_BOUNCE_PERIOD = 30
CURSOR_SLIDE_DURATION = 4
PADDING = 24
PADDING_TOP = 36
OPTIONS_X = WINDOW_WIDTH * 2 / 5
CONTROL_OFFSET = 8
CONTROLS_VISIBLE = (WINDOW_HEIGHT - PADDING * 2 - PADDING_TOP) // LINE_HEIGHT - 2
PLUS_SPACING = 2
CONTROL_SPACING = 8

def is_valid_button(button):
  return True # type(button) in (str, list)

class EnterAnim(Anim): blocking = True
class ExitAnim(Anim): blocking = True
class CursorSlideAnim(TweenAnim): blocking = False
class CursorBounceAnim(SineAnim):
  period = CURSOR_BOUNCE_PERIOD

class ControlsContext(Context):
  def __init__(ctx, bg=False, *args, **kwargs):
    super().__init__(*args, **kwargs)
    ctx.preset = copy(gamepad.controls)
    ctx.waiting = None
    ctx.button_combo = []
    ctx.multi_mode = False
    ctx.exiting = False
    ctx.scroll_index = 0
    ctx.scroll_index_drawn = 0
    ctx.cursor_index = 0
    ctx.title = Title(text="CONTROLS")
    ctx.bg = Bg(WINDOW_SIZE) if bg else None
    ctx.anims = [CursorBounceAnim()]
    ctx.controls = [
      Control(key=("Select",), value="Reset"),
      Control(key=("Tab",), value="Multi"),
    ]
    ctx.buttons_rejected = set()

  @property
  def wait_timeout(ctx):
    return (5 - (get_ticks() - ctx.waiting) // 1000) if ctx.waiting else None

  def enter(ctx):
    ctx.exiting = False
    ctx.title.enter()
    ctx.bg and ctx.bg.enter()
    ctx.anims.append(EnterAnim(duration=len(controls)))

  def exit(ctx):
    ctx.exiting = True
    ctx.title.exit(on_end=ctx.close)
    ctx.bg and ctx.bg.exit()
    ctx.anims.append(ExitAnim(duration=CONTROLS_VISIBLE))

  def close(ctx):
    super().close(ctx.preset)

  def handle_press(ctx, button):
    if ctx.exiting or next((a for a in ctx.anims if a.blocking), None):
      return False

    if ctx.child:
      return ctx.child.handle_press(button)

    press_time = keyboard.get_state(button) or gamepad.get_state(button)

    if press_time == 1 and ctx.waiting:
      if button == pygame.K_ESCAPE:
        return ctx.handle_endconfig()
      elif is_valid_button(button) and button not in ctx.button_combo:
        return ctx.button_combo.append(button)
      else:
        return None

    if button == pygame.K_TAB and not ctx.waiting:
      multi_control = next((c for c in ctx.controls if c.value == "Multi"), None)
      multi_control and multi_control.press()

    if button == pygame.K_BACKSPACE and not ctx.waiting:
      reset_control = next((c for c in ctx.controls if c.value == "Reset"), None)
      reset_control and reset_control.press()

    if (press_time == 1
    or press_time > 30 and press_time % 2):
      if button in (pygame.K_UP, gamepad.controls.UP):
        return ctx.handle_move(delta=-1)
      if button in (pygame.K_DOWN, gamepad.controls.DOWN):
        return ctx.handle_move(delta=1)

    if press_time > 1:
      return

    if button == pygame.K_DELETE:
      return ctx.handle_config(button=None)

    if button in (pygame.K_SPACE, pygame.K_RETURN, gamepad.START):
      ctx.buttons_rejected.add(button)
      return ctx.handle_startconfig()

    if button in (pygame.K_TAB, gamepad.controls.equip):
      ctx.buttons_rejected.add(button)
      return ctx.handle_multiconfig()

    if button in (pygame.K_BACKSPACE, gamepad.controls.minimap):
      return ctx.handle_reset()

    if button in (pygame.K_ESCAPE, gamepad.controls.cancel):
      return ctx.handle_close()

  def handle_release(ctx, button):
    if button == pygame.K_TAB:
      multi_control = next((c for c in ctx.controls if c.value == "Multi"), None)
      multi_control and multi_control.release()

    if button == pygame.K_BACKSPACE:
      reset_control = next((c for c in ctx.controls if c.value == "Reset"), None)
      reset_control and reset_control.release()

    if button in ctx.buttons_rejected:
      ctx.buttons_rejected.remove(button)
      return False

    if ctx.waiting and is_valid_button(button):
      ctx.buttons_rejected |= {b for b in ctx.button_combo if b != button}
      button = ctx.button_combo if len(ctx.button_combo) > 1 else ctx.button_combo[0]
      return ctx.handle_config(button)

  def handle_move(ctx, delta):
    old_index = ctx.cursor_index
    ctx.cursor_index += delta
    if ctx.cursor_index < 0:
      ctx.cursor_index = 0
      return False
    elif ctx.cursor_index > len(controls) - 1:
      ctx.cursor_index = len(controls) - 1
      return False

    ctx.scroll_index = max(0, min(len(controls) - 1 - CONTROLS_VISIBLE, ctx.cursor_index - CONTROLS_VISIBLE // 2))
    ctx.anims.append(CursorSlideAnim(
      target=(old_index, ctx.cursor_index),
      duration=CURSOR_SLIDE_DURATION
    ))
    return True

  def handle_startconfig(ctx):
    ctx.waiting = get_ticks()
    for control in ctx.controls:
      control.disable()

  def handle_multiconfig(ctx):
    ctx.handle_startconfig()
    ctx.multi_mode = True

  def handle_endconfig(ctx):
    ctx.waiting = None
    ctx.button_combo = []
    for control in ctx.controls:
      control.enable()
    return True

  def handle_config(ctx, button):
    ctx.handle_endconfig()
    if ctx.config_control(controls[ctx.cursor_index][0], button):
      if not ctx.handle_move(delta=1):
        ctx.multi_mode = False
      if ctx.multi_mode:
        ctx.handle_startconfig()
      return True
    else:
      return False

  def config_control(ctx, control, button):
    if button is None:
      button = ""

    if is_valid_button(button):
      setattr(ctx.preset, control, button)
      gamepad.config(preset=ctx.preset)
      return True
    else:
      return False

  def handle_reset(ctx):
    for control in ctx.controls:
      control.disable()
    ctx.open(PromptContext("Reset controls to defaults?", [
      Choice("Yes"),
      Choice("No", default=True)
    ]), on_close=lambda choice: (
      choice and choice.text == "Yes" and ctx.reset_controls(),
      [c.enable() for c in ctx.controls]
    ))

  def reset_controls(ctx):
    ctx.preset = copy(TYPE_A)
    ctx.reset_scroll()

  def reset_scroll(ctx):
    ctx.scroll_index = 0
    ctx.scroll_index_drawn = 0
    ctx.cursor_index = 0

  def handle_close(ctx):
    ctx.open(PromptContext("Is this setup OK?", [
      Choice("Yes"),
      Choice("No", default=True)
    ]), on_close=lambda choice: (
      choice and choice.text == "Yes" and ctx.exit()
    ))
    return True

  def update(ctx):
    super().update()
    ctx.scroll_index_drawn += (ctx.scroll_index - ctx.scroll_index_drawn) / 4
    for anim in ctx.anims:
      if not anim.done:
        anim.update()
      else:
        ctx.anims.remove(anim)

    ctx.title.update()

    if ctx.wait_timeout == 0 and not ctx.button_combo:
      ctx.waiting = None

  def view(ctx):
    sprites = []

    if ctx.bg:
      sprites += ctx.bg.view()

    # controls
    max_scroll = min(len(controls), ctx.scroll_index + CONTROLS_VISIBLE + 1)

    enter_anim = next((a for a in ctx.anims if type(a) is EnterAnim), None)
    if enter_anim:
      max_scroll = min(enter_anim.time, max_scroll)

    exit_anim = next((a for a in ctx.anims if type(a) is ExitAnim), None)
    if exit_anim:
      max_scroll = max(ctx.scroll_index, max_scroll - exit_anim.time)
    elif ctx.exiting:
      max_scroll = 0

    for i in range(ctx.scroll_index, max_scroll):
      control_id, control_name = controls[i]
      is_control_selected = i == ctx.cursor_index and ctx.waiting
      control_y = (i - ctx.scroll_index_drawn) * LINE_HEIGHT + PADDING + PADDING_TOP + font.height() / 2
      if control_y < PADDING + PADDING_TOP or control_y > WINDOW_HEIGHT - PADDING:
        continue
      control_color = GOLD if is_control_selected else WHITE
      button = is_control_selected and ctx.button_combo or getattr(ctx.preset, control_id)
      button_image = (
        font.render(f"Waiting for input... ({ctx.wait_timeout})")
          if is_control_selected and not ctx.button_combo
          else render_button(button, mappings=(None if control_id == control_id.upper() else ctx.preset.__dict__), color=(
            GOLD
              if is_control_selected and ctx.button_combo
              else GREEN
                if control_id in hold_controls
                else BLUE
          )) or font.render("-", color=GRAY)
      )
      control_image = font.render(control_name, color=control_color)
      if ctx.waiting and ctx.multi_mode and i > ctx.cursor_index:
        control_image = darken_image(control_image)
        button_image = darken_image(button_image)
      sprites += [
        Sprite(
          image=control_image,
          pos=(OPTIONS_X, control_y),
          origin=Sprite.ORIGIN_RIGHT
        ),
        *([Sprite(
          image=button_image,
          pos=(OPTIONS_X + CONTROL_OFFSET, control_y),
          origin=Sprite.ORIGIN_LEFT
        )] if button_image else [])
      ]

    if not ctx.child and not next((a for a in ctx.anims + ctx.title.anims if a.blocking), None):
      # cursor
      cursor_bounce_anim = next((a for a in ctx.anims if type(a) is CursorBounceAnim), None)
      cursor_slide_anim = next((a for a in ctx.anims if type(a) is CursorSlideAnim), None)
      if cursor_slide_anim:
        old_index, new_index = cursor_slide_anim.target
        cursor_x = lerp(
          a=font.width(controls[old_index][1]),
          b=font.width(controls[new_index][1]),
          t=cursor_slide_anim.pos
        )
        cursor_y = lerp(old_index, new_index, cursor_slide_anim.pos)
      else:
        cursor_x = font.width(controls[ctx.cursor_index][1])
        cursor_y = ctx.cursor_index
      cursor_x = -cursor_x + OPTIONS_X + CURSOR_OFFSET
      cursor_x += cursor_bounce_anim.pos * CURSOR_BOUNCE_AMP
      cursor_y -= ctx.scroll_index_drawn
      cursor_y *= LINE_HEIGHT
      cursor_y += PADDING + PADDING_TOP + font.height() / 2
      cursor_image = flip(assets.sprites["hand"], True, False)
      sprites.append(Sprite(
        image=cursor_image,
        pos=(cursor_x, cursor_y),
        origin=Sprite.ORIGIN_RIGHT
      ))

      # controls
      controls_x = WINDOW_WIDTH - 24
      controls_y = WINDOW_HEIGHT - 20
      for control in ctx.controls:
        control_image = control.render()
        sprites.append(Sprite(
          image=control_image,
          pos=(controls_x, controls_y),
          origin=Sprite.ORIGIN_RIGHT
        ))
        controls_x -= control_image.get_width() + CONTROL_SPACING

    sprites += ctx.title.view()

    for sprite in sprites:
      if not sprite.layer:
        sprite.layer = "ui"

    return sprites + super().view()

def render_button(button, mappings=None, color=BLUE):
  if type(button) is str:
    button_id = next((k.lower() for k, v in mappings.items() if v == button), button) if mappings else button
    if f"button_{button_id}" in assets.sprites:
      return replace_color(assets.sprites[f"button_{button_id}"], BLACK, color)
  elif type(button) is list:
    return render_buttons(buttons=button, mappings=mappings, color=color)
  return font.render(f"[{str(button).upper()}]")

def render_buttons(buttons, mappings, color=BLUE):
  button_images = [render_button(button=b, mappings=mappings, color=color) for b in buttons]
  plus_image = font.render("+")
  plus_width = plus_image.get_width() * (len(button_images) - 1)
  buttons_width = sum([b.get_width() if b else 0 for b in button_images]) + plus_width + PLUS_SPACING * max(2, len(button_images) * 2 - 1)
  buttons_height = button_images[0].get_height() if button_images and button_images[0] else 0
  if not buttons_width or not buttons_height:
    return None
  buttons_surface = Surface((buttons_width, buttons_height), flags=SRCALPHA)
  buttons_x = 0
  for i, button_image in enumerate(button_images):
    if i:
      buttons_surface.blit(plus_image, (buttons_x, buttons_height / 2 - plus_image.get_height() / 2))
      buttons_x += plus_image.get_width() + PLUS_SPACING
    if button_image:
      buttons_surface.blit(button_image, (buttons_x, 0))
      buttons_x += button_image.get_width() + PLUS_SPACING
  return buttons_surface
