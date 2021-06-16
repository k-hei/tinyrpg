from contexts import Context
from contexts.app import App
from comps.portraitgroup import PortraitGroup
from portraits.husband import HusbandPortrait
from portraits.wife import WifePortrait
import pygame
import keyboard

class PortraitsContext(Context):
  def __init__(ctx, portraits):
    super().__init__()
    ctx.group = PortraitGroup(portraits)

  def handle_keydown(ctx, key):
    if key == pygame.K_SPACE and keyboard.get_pressed(key) == 1:
      ctx.group.cycle()

  def view(ctx, sprites):
    ctx.group.view(sprites)

App(
  size=(256, 128),
  title="portrait group demo",
  context=PortraitsContext([
    HusbandPortrait(),
    WifePortrait()
  ])
).init()
