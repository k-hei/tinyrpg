import pygame
from contexts.app import App
from contexts import Context
from comps.card import Card
import keyboard

class CardContext(Context):
  def __init__(ctx):
    super().__init__()
    ctx.card = Card("buy")

  def handle_keydown(ctx, key):
    if keyboard.get_pressed(key) > 1:
      return

    if key == pygame.K_SPACE:
      ctx.card.spin()

  def draw(ctx, surface):
    ctx.card.render().draw(surface, (surface.get_width() // 2, surface.get_height() // 2))

App(
  title="card demo",
  size=(48, 64),
  context=CardContext()
).init()
