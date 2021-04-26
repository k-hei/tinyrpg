from math import pi, sin
import pygame
import config
import keyboard
from contexts import Context
from comps.log import Log
from assets import load as use_assets

class DialogueContext(Context):
  def __init__(ctx, parent, script):
    super().__init__(parent)
    ctx.script = script
    ctx.index = 0
    ctx.log = Log(autohide=False)
    ctx.print()

  def print(ctx):
    name, page = ctx.script[ctx.index]
    if ctx.index == 0:
      ctx.log.print(name.upper() + ": " + page)
    else:
      ctx.log.clear()
      ctx.log.print(page)

  def handle_keydown(ctx, key):
    if keyboard.get_pressed(key) != 1:
      return
    if key in (pygame.K_SPACE, pygame.K_RETURN):
      ctx.handle_next()

  def handle_next(ctx):
    if not ctx.log.clean:
      return
    ctx.index += 1
    if ctx.index == len(ctx.script):
      ctx.log.exit(on_end=ctx.close)
    else:
      ctx.print()

  def draw(ctx, surface):
    assets = use_assets()
    sprite_arrow = assets.sprites["arrow_dialogue"]
    ctx.log.update()
    sprite = ctx.log.box
    if sprite:
      x = config.WINDOW_WIDTH // 2 - sprite.get_width() // 2
      y = surface.get_height() + ctx.log.y
      surface.blit(sprite, (x, y))
      if ctx.log.clean:
        t = ctx.log.clean % 30 / 30
        offset = sin(t * 2 * pi) * 1.25
        x += -sprite_arrow.get_width() + sprite.get_width() - Log.PADDING_X - 8
        y += -sprite_arrow.get_height() + sprite.get_height() - Log.PADDING_Y + 4 + offset
        surface.blit(sprite_arrow, (x, y))
