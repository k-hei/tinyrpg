from math import sin, pi
from functools import partial
import pygame
from pygame import Surface, SRCALPHA
from pygame.transform import rotate
import lib.keyboard as keyboard
import lib.gamepad as gamepad
from lib.lerp import lerp
from easing.expo import ease_out
from colors.palette import RED, BLUE
from config import WINDOW_WIDTH, WINDOW_HEIGHT

from contexts import Context
from comps.card import Card, CARD_BUY, CARD_SELL, CARD_EXIT
from assets import load as use_assets
from lib.sprite import Sprite
from lib.filters import darken_image
from anims.tween import TweenAnim

CARD_LIFT = 4
CARD_SPACING = 2
CARD_COLORS = {
  CARD_BUY: BLUE,
  CARD_SELL: BLUE,
  CARD_EXIT: RED
}

class SelectAnim(TweenAnim): blocking = False
class DeselectAnim(TweenAnim): blocking = False
class SlideAnim(TweenAnim): blocking = True
class SlideCornerAnim(TweenAnim): blocking = True
class ChooseAnim(TweenAnim): blocking = False
class UnchooseAnim(TweenAnim): blocking = True

class CardContext(Context):
  def __init__(ctx, pos, cards, on_select=None, on_choose=None):
    super().__init__()
    ctx.pos = pos
    ctx.on_select = on_select
    ctx.on_choose = on_choose
    ctx.cards = list(map(lambda card_name: Card(
      name=card_name,
      flipped=True,
      color=CARD_COLORS[card_name]
    ), cards))
    ctx.card_index = 0
    ctx.hand_index = 0
    ctx.chosen = False
    ctx.exiting = False
    ctx.anims = []
    ctx.on_animate = None
    ctx.ticks = 0

  def card(ctx):
    return ctx.cards[ctx.card_index]

  def focus(ctx):
    ctx.chosen = False
    for card in ctx.cards:
      if card.exiting:
        card.enter()
      else:
        ctx.anims.append(UnchooseAnim(duration=20, target=card))

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
    ctx.on_animate = lambda: ctx.on_select(ctx.card())

  def exit(ctx):
    ctx.exiting = True
    for card in ctx.cards:
      if not card.exiting:
        card.warp()

  def handle_press(ctx, button):
    if ctx.child:
      return ctx.child.handle_press(button)

    if (next((c for c in ctx.cards if c.anims), None)
    or next((a for a in ctx.anims if a.blocking), None)
    or ctx.chosen):
      return False

    if keyboard.get_state(button) > 1 or gamepad.get_state(button) > 1:
      return

    if button in (pygame.K_LEFT, pygame.K_a, gamepad.controls.LEFT):
      ctx.handle_move(-1)
    if button in (pygame.K_RIGHT, pygame.K_d, gamepad.controls.RIGHT):
      ctx.handle_move(1)
    if button in (pygame.K_RETURN, pygame.K_SPACE, gamepad.controls.confirm):
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
    if ctx.on_select:
      ctx.on_select(ctx.card())

  def handle_choose(ctx):
    card = ctx.card()
    ctx.chosen = True
    def end():
      ctx.on_choose(card)
    card.spin(on_end=end)
    ctx.anims.append(ChooseAnim(duration=20, target=card))
    for c in ctx.cards:
      if c is not card:
        c.exit()

  def update(ctx):
    super().update()
    for anim in ctx.anims:
      if anim.done:
        ctx.anims.remove(anim)
        if (anim.blocking
        and not next((a for a in ctx.anims if a.blocking), None)
        and ctx.on_animate):
          ctx.on_animate()
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
    card_sprites = []
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
          elif type(card_anim) is ChooseAnim:
            t = ease_out(t)
            card_y -= CARD_LIFT + CARD_LIFT * 2 * t
          elif type(card_anim) is UnchooseAnim:
            t = 1 - t
            card_y -= CARD_LIFT + CARD_LIFT * 2 * t
          elif type(card_anim) is SlideAnim:
            t = ease_out(t)
            from_x = WINDOW_WIDTH - 4 - card_template.get_width() // 2
            from_y = 4 + card_template.get_height() // 2
            card_x = lerp(from_x, card_x, t)
            card_y = lerp(from_y, card_y, t)
        if card is not ctx.card():
          card_sprite.image = darken_image(card_sprite.image)
        elif not ctx.anims and not ctx.chosen:
          card_y -= CARD_LIFT
        elif not ctx.anims and ctx.chosen:
          card_y -= CARD_LIFT * 3
        card_sprite.move((card_x, card_y))
        card_sprites.insert(0, card_sprite)
      x += card_template.get_width() + CARD_SPACING
    sprites += card_sprites
    if (not next((a for a in ctx.anims if a.blocking), None)
    and not (ctx.chosen and ctx.ticks % 2)
    and not (ctx.chosen and not ctx.card().anims)
    and not ctx.exiting):
      hand_image = rotate(assets["hand"], -90)
      hand_x = cards_x + ctx.hand_index * (card_template.get_width() + CARD_SPACING) + card_template.get_width() / 2
      hand_y = cards_y + card_template.get_height() / 2 + 5
      if not ctx.chosen:
        hand_y += sin(ctx.ticks % 30 / 30 * 2 * pi) * 1.5
      sprites.append(Sprite(
        image=hand_image,
        pos=(hand_x, hand_y),
        origin=("center", "center"),
        layer="hud"
      ))
    return sprites

  def draw(ctx, surface):
    Sprite(
      image=ctx.render(),
      pos=surface.get_rect().center,
      origin=("center", "center")
    ).draw(surface)
