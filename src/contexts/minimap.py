import pygame
from contexts import Context
from comps.minimap import Minimap
from comps.hud import Hud
from comps.previews import Previews
from comps.spmeter import SpMeter
from comps.floorno import FloorNo

class MinimapContext(Context):
  effects = [Hud, Previews, SpMeter, FloorNo]

  def __init__(ctx, minimap, on_close=None):
    super().__init__(on_close=on_close)
    ctx.minimap = minimap

  def enter(ctx):
    ctx.minimap.expand()

  def exit(ctx):
    ctx.minimap.shrink()
    ctx.close()

  def handle_keydown(ctx, key):
    if ctx.minimap.anims:
      return False

    if key == pygame.K_BACKSPACE or key == pygame.K_ESCAPE:
      return ctx.handle_close()

  def handle_close(ctx):
    ctx.exit()
    return True
