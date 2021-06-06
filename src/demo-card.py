import pygame
from pygame import Surface
from contexts.app import App
from contexts import Context
from comps.card import Card
from assets import load as use_assets
from palette import RED
from sprite import Sprite
from filters import darken
import keyboard

CARD_SPACING = 2

class CardContext(Context):
  def __init__(ctx):
    super().__init__()
    ctx.surface = None
    ctx.card_index = 0
    ctx.cards = [
      Card("buy"),
      Card("sell"),
      Card("exit", color=RED)
    ]

  def card(ctx):
    return ctx.cards[ctx.card_index]

  def handle_keydown(ctx, key):
    if keyboard.get_pressed(key) > 1:
      return

    if key in (pygame.K_LEFT, pygame.K_a):
      ctx.handle_move(-1)
    if key in (pygame.K_RIGHT, pygame.K_d):
      ctx.handle_move(1)
    if key in (pygame.K_RETURN, pygame.K_SPACE):
      ctx.card().spin()

  def handle_move(ctx, delta):
    ctx.card_index += delta
    if ctx.card_index < 0:
      ctx.card_index = 0
    if ctx.card_index > len(ctx.cards) - 1:
      ctx.card_index = len(ctx.cards) - 1

  def render(ctx):
    sprites = use_assets().sprites
    card_template = sprites["card_back"]
    ctx.surface = Surface((
      len(ctx.cards) * (card_template.get_width() + CARD_SPACING) - CARD_SPACING,
      card_template.get_height()
    ))
    card_x = 0
    for card in ctx.cards:
      card_sprite = card.render()
      if card is not ctx.card():
        card_sprite.image = darken(card_sprite.image)
      card_sprite.draw(ctx.surface, (card_x, 0), origin=("left", "top"))
      card_x += card_template.get_width() + CARD_SPACING
    return ctx.surface

  def draw(ctx, surface):
    Sprite(
      image=ctx.render(),
      pos=surface.get_rect().center,
      origin=("center", "center")
    ).draw(surface)

App(
  title="card demo",
  size=(100, 48),
  context=CardContext()
).init()
