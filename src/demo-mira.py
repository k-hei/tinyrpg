import pygame
from contexts import Context
from contexts.app import App
from assets import load as use_assets
from palette import WHITE
from anims.frame import FrameAnim
from portraits.mira import MiraPortrait
import keyboard

class PortraitContext(Context):
  def __init__(ctx):
    super().__init__()
    ctx.portrait = MiraPortrait()

  def handle_keydown(ctx, key):
    if keyboard.get_pressed(key) > 1:
      return

    if key == pygame.K_SPACE:
      return ctx.portrait.start_talk() if not ctx.portrait.talking else ctx.portrait.stop_talk()

  def draw(ctx, surface):
    surface.fill(WHITE)
    portrait = ctx.portrait.render()
    surface.blit(portrait, (0, 0))

App(
  size=(160, 128),
  title="mira portrait demo",
  context=PortraitContext()
).init()
