from math import sin, cos, pi
import pygame
from pygame import Rect
from pygame.transform import rotate, scale
from contexts import Context
from contexts.sell import SellContext
from cores.knight import KnightCore
from comps.control import Control
from comps.card import Card
from hud import Hud
from assets import load as use_assets
from filters import replace_color, darken
from palette import BLACK, WHITE, RED, BLUE, GOLD
import keyboard
from anims import Anim
from anims.tween import TweenAnim
from easing.expo import ease_out
from lib.lerp import lerp

class CursorAnim(Anim): blocking = False
class SelectAnim(TweenAnim): blocking = False
class DeselectAnim(TweenAnim): blocking = False
class TwirlAnim(TweenAnim): pass

class ShopContext(Context):
  def __init__(ctx, items):
    super().__init__()
    ctx.items = items
    ctx.cards = [Card("buy"), Card("sell"), Card("exit", color=RED)]
    ctx.card_index = 0
    ctx.hand_index = 0
    ctx.card_pos = {}
    ctx.hero = KnightCore()
    ctx.hud = Hud()
    ctx.anims = [CursorAnim()]
    ctx.controls = [
      Control(key=("X"), value="Menu")
    ]

  def handle_keydown(ctx, key):
    if ctx.child:
      return ctx.child.handle_keydown(key)

    if next((a for a in ctx.anims if a.blocking), None):
      return False

    if keyboard.get_pressed(key) > 1:
      return

    if key in (pygame.K_LEFT, pygame.K_a):
      return ctx.handle_move(-1)
    if key in (pygame.K_RIGHT, pygame.K_d):
      return ctx.handle_move(1)
    if key in (pygame.K_SPACE, pygame.K_RETURN):
      return ctx.handle_select()

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
      return False
    ctx.card_index = new_index
    ctx.anims.append(DeselectAnim(
      duration=8,
      target=old_index
    ))
    ctx.anims.append(SelectAnim(
      duration=12,
      target=new_index
    ))
    return True

  def handle_select(ctx):
    option = ctx.cards[ctx.card_index]
    ctx.anims.append(TwirlAnim(
      duration=20,
      target=ctx.card_index,
      on_end=lambda: (
        option == "buy" and True
        or option == "sell" and ctx.handle_sell()
        or option == "exit" and True
      )
    ))

  def handle_sell(ctx):
    option = ctx.cards[ctx.card_index]
    ctx.open(SellContext(
      items=ctx.items,
      card_pos=ctx.card_pos[option]
    ))

  def update(ctx):
    super().update()
    ctx.hand_index += (ctx.card_index - ctx.hand_index) / 4
    for anim in ctx.anims:
      if anim.done:
        ctx.anims.remove(anim)
      else:
        anim.update()

  def draw(ctx, surface):
    assets = use_assets()
    surface.fill(WHITE)
    pygame.draw.rect(surface, BLACK, Rect(0, 112, 256, 112))

    MARGIN = 2

    # tagbg_image = assets.sprites["shop_tag"]
    # tagbg_x = surface.get_width() - tagbg_image.get_width()
    # tagbg_y = 0
    # surface.blit(tagbg_image, (tagbg_x, tagbg_y))

    # tagtext_image = assets.sprites["general_store"]
    # tagtext_x = surface.get_width() - tagtext_image.get_width() - 2
    # tagtext_y = tagbg_y + tagbg_image.get_height() // 2 - tagtext_image.get_height() // 2
    # surface.blit(tagtext_image, (tagtext_x, tagtext_y))

    hud_image = ctx.hud.update(ctx.hero)
    hud_x = MARGIN
    hud_y = surface.get_height() - hud_image.get_height() - MARGIN
    surface.blit(hud_image, (hud_x, hud_y))

    gold_image = assets.sprites["item_gold"]
    gold_image = replace_color(gold_image, BLACK, GOLD)
    gold_x = hud_x + hud_image.get_width() + 2
    gold_y = hud_y + hud_image.get_height() - gold_image.get_height() - 2
    surface.blit(gold_image, (gold_x, gold_y))

    goldtext_font = assets.ttf["roman"]
    goldtext_image = goldtext_font.render("500")
    goldtext_x = gold_x + gold_image.get_width() + 3
    goldtext_y = gold_y + gold_image.get_height() // 2 - goldtext_image.get_height() // 2
    surface.blit(goldtext_image, (goldtext_x, goldtext_y))

    CARD_MARGIN = 8
    CARD_SPACING = 2
    CARD_LIFT = 4
    CARD_WIDTH = assets.sprites["card_back"].get_width()
    CARD_HEIGHT = assets.sprites["card_back"].get_height()
    cards_x = 40
    cards_y = 120
    for i, card in enumerate(ctx.cards):
      card_sprite = card.render()
      card_sprite.draw(surface, (cards_x + (CARD_WIDTH + 2) * i, cards_y))

    title_image = assets.ttf["english_large"].render("General Store")
    title_x = surface.get_width() - title_image.get_width() - CARD_MARGIN
    title_y = surface.get_height() - title_image.get_height() - 7
    surface.blit(title_image, (title_x, title_y))

    hand_anim = next((a for a in ctx.anims if type(a) is CursorAnim), None)
    hand_image = assets.sprites["hand"]
    hand_image = rotate(hand_image, -90)
    hand_x = cards_x
    hand_x -= hand_image.get_width() // 2
    hand_x += (CARD_WIDTH + CARD_SPACING) * ctx.hand_index
    hand_y = cards_y
    hand_y += CARD_HEIGHT // 2
    hand_y += sin(hand_anim.time % 30 / 30 * 2 * pi) * 2
    surface.blit(hand_image, (hand_x, hand_y))

    # subtitle_text = assets.ttf["roman"].render("Exchange money for goods and services")
    # subtitle_x = title_x + title_text.get_width() - subtitle_text.get_width()
    # subtitle_y = title_y - title_text.get_height() + 4
    # surface.blit(subtitle_text, (subtitle_x, subtitle_y))

    # controls_x = surface.get_width() - 8
    # controls_y = surface.get_height() - 12
    # for control in ctx.controls:
    #   control_image = control.render()
    #   control_x = controls_x - control_image.get_width()
    #   control_y = controls_y - control_image.get_height() // 2
    #   surface.blit(control_image, (control_x, control_y))
    #   controls_x = control_x - 8

    if ctx.child:
      ctx.child.draw(surface)
