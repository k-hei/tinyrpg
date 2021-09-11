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

  def enter(ctx):
    ctx.group.enter()

  def update(ctx):
    ctx.group.update()

  def handle_press(ctx, key):
    if ctx.group.anims or keyboard.get_pressed(key) > 1:
      return
    if key == pygame.K_TAB:
      return ctx.group.cycle()
    if key == pygame.K_ESCAPE:
      return ctx.group.stop_cycle()

  def view(ctx):
    return ctx.group.view() + super().view()

App(
  size=(256, 128),
  title="portrait group demo",
  context=PortraitsContext([
    HusbandPortrait(),
    WifePortrait()
  ])
).init()
