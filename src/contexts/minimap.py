import pygame
import lib.input as input
from contexts import Context
from comps.minimap import Minimap

class MinimapContext(Context):
  def __init__(ctx, minimap, lock=False, on_close=None):
    super().__init__(on_close=on_close)
    ctx.minimap = minimap
    ctx.lock = lock

  def enter(ctx):
    minimap = ctx.minimap
    if ctx.lock:
      minimap.anims = []
      minimap.active = True
      minimap.expanded = minimap.BLACKOUT_DELAY
    else:
      minimap.expand()

  def exit(ctx):
    ctx.minimap.shrink()
    ctx.close()

  def handle_press(ctx, button):
    if ctx.minimap.anims or ctx.lock:
      return False

    if button in (pygame.K_BACKSPACE, pygame.K_ESCAPE):
      return ctx.handle_close()

  def handle_release(ctx, button):
    controls = input.resolve_controls(button)
    if input.CONTROL_MINIMAP in controls:
      return ctx.handle_close()

  def handle_close(ctx):
    ctx.exit()
    return True
