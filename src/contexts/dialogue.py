from math import pi, sin
import pygame
from pygame import Rect, Surface
import config
from config import WINDOW_WIDTH, WINDOW_HEIGHT
import keyboard
import lib.gamepad as gamepad
from contexts import Context
from assets import load as use_assets
from comps.log import Log
from collections.abc import Iterable
from colors.palette import BLACK
from anims.tween import TweenAnim
from easing.expo import ease_out
from sprite import Sprite
import debug

class EnterAnim(TweenAnim): pass
class ExitAnim(TweenAnim): pass

class DialogueContext(Context):
  BAR_HEIGHT = 24
  BAR_ENTER_DURATION = 15
  BAR_EXIT_DURATION = 7

  def __init__(ctx, script, lite=False, side="bottom", log=None, on_close=None):
    super().__init__(on_close=on_close)
    ctx.script = script
    ctx.lite = lite
    ctx.side = side
    ctx.index = 0
    ctx.name = None
    ctx.log = log or Log(autohide=False, side=side)
    ctx.anim = None

  def init(ctx):
    if callable(ctx.script):
      ctx.script = ctx.script(ctx.parent)
    elif type(ctx.script) is DialogueContext:
      ctx.parent.open(ctx.script)
    else:
      ctx.script = list(ctx.script)

  def enter(ctx):
    if ctx.lite:
      ctx.print()
    else:
      ctx.anim = EnterAnim(duration=ctx.BAR_ENTER_DURATION, on_end=ctx.print)

  def exit(ctx):
    if ctx.lite:
      ctx.log.exit(on_end=ctx.close)
    else:
      ctx.anim = ExitAnim(duration=ctx.BAR_EXIT_DURATION, on_end=ctx.close)
      ctx.log.exit()

  def print(ctx, item=None):
    if item is None:
      item = ctx.script[min(len(ctx.script) - 1, ctx.index)]

    if callable(item):
      item = item()

    if item is None or type(item) is bool:
      return ctx.handle_next()

    if isinstance(item, Context):
      def print():
        ctx.name = None
        ctx.open(item, on_close=lambda *data: (
          data and isinstance(data[0], Iterable) and ctx.script.extend(data[0]),
          ctx.handle_next()
        ))
        if "log" in dir(ctx.child):
          ctx.log.clear()
          ctx.child.log = ctx.log
          ctx.log.silent = True
          ctx.child.enter()
          ctx.log.silent = False
        else:
          ctx.log.exit()
      if ctx.name:
        print()
      else:
        ctx.log.exit(on_end=print)
      return

    ctx.log.clear()

    if type(item) is tuple:
      name, text = item
    else:
      name, text = None, item

    if callable(text):
      text = text()
    if name != ctx.name:
      ctx.name = name
      if name:
        message = (name.upper(), ": ", text)
      else:
        message = text
      if not ctx.log.active:
        ctx.log.print(message)
      else:
        ctx.log.exit(on_end=lambda: ctx.log.print(message))
    else:
      ctx.log.print(text)

  def handle_press(ctx, button):
    if ctx.anim:
      return
    if ctx.child:
      return ctx.child.handle_press(button)
    if button == gamepad.controls.cancel:
      ctx.handle_next()
    if keyboard.get_pressed(button) != 1 and gamepad.get_state(button) != 1:
      return
    if button in (pygame.K_SPACE, pygame.K_RETURN, gamepad.controls.confirm):
      ctx.handle_next()

  def handle_next(ctx):
    if not ctx.log.clean:
      return ctx.log.skip()
    ctx.index += 1
    if ctx.index >= len(ctx.script):
      return ctx.exit()
    ctx.print()

  def view(ctx):
    sprites = []
    assets = use_assets()
    sprite_arrow = assets.sprites["arrow_dialogue"]

    bar_height = ctx.BAR_HEIGHT
    if ctx.anim:
      anim = ctx.anim
      if anim.done:
        ctx.anim = None
      anim.update()
      t = anim.pos
      if type(anim) is EnterAnim:
        t = ease_out(t)
      elif type(anim) is ExitAnim:
        t = 1 - t
      bar_height *= t
    if not ctx.lite:
      bar_top = Surface((WINDOW_WIDTH, bar_height))
      bar_top.fill(BLACK)
      bar_bottom = Surface((WINDOW_WIDTH, bar_height))
      bar_bottom.fill(BLACK)
      sprites += [
        Sprite(image=bar_top, pos=(0, 0), layer="ui"),
        Sprite(image=bar_bottom, pos=(0, WINDOW_HEIGHT - bar_height + 1), layer="ui")
      ]

    if not ctx.child or not "log" in dir(ctx.child):
      log_sprites = ctx.log.view()
      if log_sprites:
        sprites += log_sprites
        log_pos = log_sprites[0].pos
        if log_pos:
          x, y = log_pos
          sprite = ctx.log.box
          if ctx.log.clean:
            t = ctx.log.clean % 30 / 30
            offset = sin(t * 2 * pi) * 1.25
            x += -sprite_arrow.get_width() + sprite.get_width() - Log.PADDING_X - 8
            y += -sprite_arrow.get_height() + sprite.get_height() - Log.PADDING_Y + 4 + offset
            sprites += [Sprite(
              image=sprite_arrow,
              pos=(x, y),
              layer="hud"
            )]
    return sprites + super().view()
