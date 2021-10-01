import pygame
from pygame.transform import flip
import lib.keyboard as keyboard
import lib.gamepad as gamepad
from lib.lerp import lerp
from contexts import Context
import assets
from game.controls import ControlPreset
from sprite import Sprite
from anims.tween import TweenAnim
from anims.sine import SineAnim
from filters import replace_color
from config import WINDOW_WIDTH, WINDOW_HEIGHT
from colors.palette import BLACK, WHITE, GRAY, BLUE, GOLD

controls = [*{
  "left": "Left",
  "right": "Right",
  "up": "Up",
  "down": "Down",
  "confirm": "Confirm",
  "cancel": "Cancel",
  "action": "Action",
  "item": "Carry/Throw",
  "wait": "Wait",
  "run": "Run",
  "turn": "Turn",
  "ally": "Switch chars",
  "skill": "Use skill",
  "inventory": "Open inventory",
  "equip": "Change equipment",
  "minimap": "View minimap"
}.items()]

font = assets.ttf["normal"]
LINE_SPACING = 8
LINE_HEIGHT = font.height() + LINE_SPACING
CURSOR_OFFSET = -4
CURSOR_BOUNCE_AMP = 2
CURSOR_BOUNCE_PERIOD = 30
CURSOR_SLIDE_DURATION = 4
PADDING = 24
OPTIONS_X = WINDOW_WIDTH * 2 / 5
CONTROL_OFFSET = 8
CONTROLS_VISIBLE = (WINDOW_HEIGHT - PADDING * 2) // LINE_HEIGHT

class CursorBounceAnim(SineAnim):
  period = CURSOR_BOUNCE_PERIOD
  blocking = False

class CursorSlideAnim(TweenAnim):
  blocking = True

class ControlsContext(Context):
  def __init__(ctx, *args, **kwargs):
    super().__init__(*args, **kwargs)
    ctx.preset = ControlPreset()
    ctx.waiting = False
    ctx.scroll_index = 0
    ctx.scroll_index_drawn = 0
    ctx.cursor_index = 0
    ctx.anims = [CursorBounceAnim()]

  def close(ctx):
    super().close(ctx.preset)

  def handle_press(ctx, button):
    press_time = keyboard.get_pressed(button) or gamepad.get_state(button)

    if ctx.waiting and press_time == 1:
      ctx.waiting = False
      print(button)
      return ctx.config_control(controls[ctx.cursor_index][0], button)

    if (press_time == 1
    or press_time > 30 and press_time % 2):
      if button == pygame.K_UP:
        return ctx.handle_move(delta=-1)
      if button == pygame.K_DOWN:
        return ctx.handle_move(delta=1)

    if press_time > 1:
      return

    if button in (pygame.K_SPACE, pygame.K_RETURN):
      ctx.waiting = True

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

  def config_control(ctx, control, button):
    setattr(ctx.preset, control, button)
    return True
    # if type(button) is str:
    # else:

  def update(ctx):
    super().update()
    ctx.scroll_index_drawn += (ctx.scroll_index - ctx.scroll_index_drawn) / 4
    for anim in ctx.anims:
      if not anim.done:
        anim.update()
      else:
        ctx.anims.remove(anim)

  def view(ctx):
    sprites = []

    # controls
    for i in range(ctx.scroll_index, min(len(controls), ctx.scroll_index + CONTROLS_VISIBLE + 1)):
      control_id, control_name = controls[i]
      is_control_selected = i == ctx.cursor_index and ctx.waiting
      control_color = GOLD if is_control_selected else WHITE
      control_y = (i - ctx.scroll_index_drawn) * LINE_HEIGHT + PADDING + font.height() / 2
      button_id = getattr(ctx.preset, control_id)
      button_name = f"button_{button_id}"
      button_image = (
        is_control_selected
          and font.render("Waiting for input...")
          or button_id and button_name in assets.sprites
            and replace_color(assets.sprites[button_name], BLACK, BLUE)
            or font.render("-", color=GRAY)
      )
      sprites += [
        Sprite(
          image=font.render(control_name, color=control_color),
          pos=(OPTIONS_X, control_y),
          origin=Sprite.ORIGIN_RIGHT
        ),
        Sprite(
          image=button_image,
          pos=(OPTIONS_X + CONTROL_OFFSET, control_y),
          origin=Sprite.ORIGIN_LEFT
        )
      ]

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
    cursor_y += PADDING + font.height() / 2
    cursor_image = flip(assets.sprites["hand"], True, False)
    sprites.append(Sprite(
      image=cursor_image,
      pos=(cursor_x, cursor_y),
      origin=Sprite.ORIGIN_RIGHT
    ))

    return sprites
