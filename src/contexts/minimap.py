import pygame
from contexts import Context
from comps.minimap import Minimap

class MinimapContext(Context):
  def __init__(ctx, parent, minimap, on_close=None):
    super().__init__(parent)
    ctx.on_close = on_close
    ctx.minimap = minimap
    ctx.anims = []
    ctx.enter()

  def enter(ctx):
    ctx.minimap.expand()

  def exit(ctx):
    ctx.minimap.shrink()
    ctx.close()

  def handle_keydown(ctx, key):
    if ctx.minimap.anims:
      return False

    if key == pygame.K_BACKSPACE or key == pygame.K_ESCAPE:
      ctx.handle_close()

  def handle_close(ctx):
    ctx.exit()
