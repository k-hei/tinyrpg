import pygame
from pygame import Surface, SRCALPHA
from contexts import Context
from comps.card import Card
from assets import load as use_assets
from palette import RED
from sprite import Sprite
from filters import darken
from anims.tween import TweenAnim
from easing.expo import ease_out
import keyboard

CARD_LIFT = 4
CARD_SPACING = 2

class SelectAnim(TweenAnim): pass
class DeselectAnim(TweenAnim): pass

class CardContext(Context):
  def __init__(ctx, on_choose=None):
    super().__init__()
    ctx.on_choose = on_choose
    ctx.card_index = 0
    ctx.cards = [
      Card("buy"),
      Card("sell"),
      Card("exit", color=RED)
    ]
    ctx.anims = []
    ctx.surface = None

  def card(ctx):
    return ctx.cards[ctx.card_index]

  def handle_keydown(ctx, key):
    if next((c for c in ctx.cards if c.anims), None):
      return False

    if keyboard.get_pressed(key) > 1:
      return

    if key in (pygame.K_LEFT, pygame.K_a):
      ctx.handle_move(-1)
    if key in (pygame.K_RIGHT, pygame.K_d):
      ctx.handle_move(1)
    if key in (pygame.K_RETURN, pygame.K_SPACE):
      ctx.handle_choose()

  def handle_move(ctx, delta):
    old_index = ctx.card_index
    new_index = old_index + delta
    min_index = 0
    max_index = len(ctx.cards) - 1
    if new_index < min_index:
      new_index = min_index
    if new_index > max_index:
      new_index = max_index
    if new_index == old_index:
      return
    ctx.anims.append(DeselectAnim(duration=6, target=ctx.card()))
    ctx.card_index = new_index
    ctx.anims.append(SelectAnim(duration=9, target=ctx.card()))

  def handle_choose(ctx):
    card = ctx.card()
    card.spin(on_end=lambda: ctx.on_choose(card))

  def update(ctx):
    for anim in ctx.anims:
      if anim.done:
        ctx.anims.remove(anim)
      else:
        anim.update()

  def view(ctx):
    sprites = []
    assets = use_assets().sprites
    card_template = assets["card_back"]
    if ctx.surface:
      ctx.surface.fill(0)
    else:
      ctx.surface = Surface((
        len(ctx.cards) * (card_template.get_width() + CARD_SPACING) - CARD_SPACING,
        card_template.get_height() + CARD_LIFT
      ), SRCALPHA)
    card_x = card_template.get_width() // 2
    for card in ctx.cards:
      card_sprite = card.render()
      card_anim = next((a for a in ctx.anims if a.target is card), None)
      card_y = 0
      if card_anim:
        t = card_anim.pos
        if type(card_anim) is SelectAnim:
          t = ease_out(t)
        elif type(card_anim) is DeselectAnim:
          t = 1 - t
        card_y = CARD_LIFT * t
      if card is not ctx.card():
        card_sprite.image = darken(card_sprite.image)
      elif card_anim is None:
        card_y = CARD_LIFT
      card_sprite.move((card_x, -card_y))
      sprites.append(card_sprite)
      card_x += card_template.get_width() + CARD_SPACING
    return sprites

  def draw(ctx, surface):
    Sprite(
      image=ctx.render(),
      pos=surface.get_rect().center,
      origin=("center", "center")
    ).draw(surface)
