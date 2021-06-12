from math import sin, pi
import pygame
from pygame import Surface, SRCALPHA
from pygame.transform import rotate
from contexts import Context
from comps.card import Card, CARD_BUY, CARD_SELL, CARD_EXIT
from assets import load as use_assets
from palette import RED, BLUE
from sprite import Sprite
from filters import darken
from anims.tween import TweenAnim
from easing.expo import ease_out
from lib.lerp import lerp
from config import WINDOW_WIDTH, WINDOW_HEIGHT
from functools import partial
import keyboard

CARD_LIFT = 4
CARD_SPACING = 2

class SelectAnim(TweenAnim): blocking = False
class DeselectAnim(TweenAnim): blocking = False
class SlideAnim(TweenAnim): blocking = True

class CardContext(Context):
  def __init__(ctx, pos, on_choose=None):
    super().__init__()
    ctx.pos = pos
    ctx.on_choose = on_choose
    ctx.cards = [
      Card(CARD_BUY, flipped=True, color=BLUE),
      Card(CARD_SELL, flipped=True, color=BLUE),
      Card(CARD_EXIT, flipped=True, color=RED)
    ]
    ctx.card_index = 0
    ctx.hand_index = 0
    ctx.chosen = False
    ctx.anims = []
    ctx.ticks = 0

  def card(ctx):
    return ctx.cards[ctx.card_index]

  def focus(ctx):
    for card in ctx.cards:
      if card.exiting:
        card.enter()

  def enter(ctx):
    SLIDE_DURATION = 5
    SLIDE_TOTAL_DURATION = len(ctx.cards) * SLIDE_DURATION
    animate = lambda i, card: (
      ctx.anims.append(SlideAnim(
        duration=10,
        delay=i * SLIDE_DURATION,
        target=card,
        on_end=partial(card.flip, delay=SLIDE_DURATION)
      ))
    )
    for i, card in enumerate(ctx.cards):
      animate(i, card)
    ctx.anims.append(SelectAnim(
      duration=9,
      delay=SLIDE_TOTAL_DURATION,
      target=ctx.card()
    ))

  def handle_keydown(ctx, key):
    if ctx.child:
      return ctx.child.handle_keydown(key)

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
    ctx.chosen = True
    def end():
      ctx.chosen = False
      ctx.on_choose(card)
    card.spin(on_end=end)
    for c in ctx.cards:
      if c is not card:
        c.exit()

  def update(ctx):
    super().update()
    for anim in ctx.anims:
      if anim.done:
        ctx.anims.remove(anim)
      else:
        anim.update()
    ctx.hand_index += (ctx.card_index - ctx.hand_index) / 4
    ctx.ticks += 1

  def view(ctx):
    if ctx.child:
      return ctx.child.view()
    sprites = []
    assets = use_assets().sprites
    card_template = assets["card_back"]
    cards_x, cards_y = ctx.pos
    x = card_template.get_width() // 2
    for card in ctx.cards:
      card_sprite = card.render()
      if card_sprite:
        card_anim = next((a for a in ctx.anims if a.target is card), None)
        card_x = cards_x + x
        card_y = cards_y
        if card_anim:
          t = card_anim.pos
          if type(card_anim) is SelectAnim:
            t = ease_out(t)
            card_y -= CARD_LIFT * t
          elif type(card_anim) is DeselectAnim:
            t = 1 - t
            card_y -= CARD_LIFT * t
          elif type(card_anim) is SlideAnim:
            t = ease_out(t)
            from_x = WINDOW_WIDTH - 4 - card_template.get_width() // 2
            from_y = 4 + card_template.get_height() // 2
            card_x = lerp(from_x, card_x, t)
            card_y = lerp(from_y, card_y, t)
        if card is not ctx.card():
          card_sprite.image = darken(card_sprite.image)
        elif not ctx.anims:
          card_y -= CARD_LIFT
        card_sprite.move((card_x, card_y))
        sprites.insert(0, card_sprite)
      x += card_template.get_width() + CARD_SPACING
    if (not next((a for a in ctx.anims if a.blocking), None)
    and not (ctx.chosen and ctx.ticks % 2)):
      hand_image = rotate(assets["hand"], -90)
      hand_x = cards_x + ctx.hand_index * (card_template.get_width() + CARD_SPACING) + card_template.get_width() / 2
      hand_y = cards_y + card_template.get_height() / 2 + 5
      if not ctx.chosen:
        hand_y += sin(ctx.ticks % 30 / 30 * 2 * pi) * 1.5
      sprites.append(Sprite(
        image=hand_image,
        pos=(hand_x, hand_y),
        origin=("center", "center")
      ))
    return sprites

  def draw(ctx, surface):
    Sprite(
      image=ctx.render(),
      pos=surface.get_rect().center,
      origin=("center", "center")
    ).draw(surface)
