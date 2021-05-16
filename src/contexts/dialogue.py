from math import pi, sin
import pygame
import config
import keyboard
from contexts import Context
from assets import load as use_assets
from comps.log import Log
from hud import Hud
# from comps.previews import Previews
# from comps.minimap import Minimap
# from comps.spmeter import SpMeter
# from comps.floorno import FloorNo

class DialogueContext(Context):
  effects = [Hud] # , Previews, Minimap, SpMeter, FloorNo]

  def __init__(ctx, script, on_close=None):
    super().__init__(on_close=on_close)
    ctx.script = script
    ctx.index = 0
    ctx.name = None
    ctx.log = Log(autohide=False)
    ctx.print()

  def print(ctx, item=None):
    if item is None:
      item = ctx.script[min(len(ctx.script) - 1, ctx.index)]
    if isinstance(item, Context):
      ctx.log.exit()
      return ctx.open(item, on_close=lambda _: ctx.handle_next())
    ctx.log.clear()
    if type(item) is tuple:
      name, page = item
    else:
      name, page = None, item
    if callable(page):
      page = page()
    if name and name != ctx.name:
      ctx.name = name
      ctx.log.print(name.upper() + ": " + page)
    else:
      ctx.log.print(page)

  def handle_keydown(ctx, key):
    if ctx.child:
      return ctx.child.handle_keydown(key)
    if keyboard.get_pressed(key) != 1:
      return
    if key in (pygame.K_SPACE, pygame.K_RETURN):
      ctx.handle_next()

  def handle_next(ctx):
    if not ctx.log.clean:
      return ctx.log.skip()
    ctx.index += 1
    if ctx.index == len(ctx.script):
      return ctx.log.exit(on_end=ctx.close)
    ctx.print()

  def draw(ctx, surface):
    assets = use_assets()
    sprite_arrow = assets.sprites["arrow_dialogue"]
    ctx.log.update()
    sprite = ctx.log.box
    if sprite:
      x = config.WINDOW_WIDTH // 2 - sprite.get_width() // 2
      y = surface.get_height() - ctx.log.y
      surface.blit(sprite, (x, y))
      if ctx.log.clean:
        t = ctx.log.clean % 30 / 30
        offset = sin(t * 2 * pi) * 1.25
        x += -sprite_arrow.get_width() + sprite.get_width() - Log.PADDING_X - 8
        y += -sprite_arrow.get_height() + sprite.get_height() - Log.PADDING_Y + 4 + offset
        surface.blit(sprite_arrow, (x, y))
    super().draw(surface)
