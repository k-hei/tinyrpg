import pygame
from pygame import Rect
from contexts import Context
from contexts.sell import SellContext
from cores.knight import KnightCore
from comps.control import Control
from hud import Hud
from assets import load as use_assets
from filters import replace_color, darken
from palette import BLACK, WHITE, RED, BLUE, GOLD
import keyboard

class ShopContext(Context):
  def __init__(ctx):
    super().__init__()
    ctx.option_index = 0
    ctx.options = ["buy", "sell", "exit"]
    ctx.hero = KnightCore()
    ctx.hud = Hud()
    ctx.controls = [
      Control(key=("X"), value="Menu")
    ]

  def handle_keydown(ctx, key):
    if keyboard.get_pressed(key) > 1:
      return

    if key in (pygame.K_LEFT, pygame.K_a):
      return ctx.handle_move(-1)
    if key in (pygame.K_RIGHT, pygame.K_d):
      return ctx.handle_move(1)

  def handle_move(ctx, delta):
    old_index = ctx.option_index
    new_index = old_index + delta
    min_index = 0
    max_index = len(ctx.options) - 1
    if new_index < min_index:
      new_index = min_index
    if new_index > max_index:
      new_index = max_index
    if new_index == old_index:
      return False
    ctx.option_index = new_index
    return True

  def draw(ctx, surface):
    assets = use_assets()
    surface.fill(WHITE)
    pygame.draw.rect(surface, BLACK, Rect(0, 112, 256, 112))

    MARGIN = 2

    tagbg_image = assets.sprites["shop_tag"]
    tagbg_x = surface.get_width() - tagbg_image.get_width()
    tagbg_y = 0
    surface.blit(tagbg_image, (tagbg_x, tagbg_y))

    tagtext_image = assets.sprites["general_store"]
    tagtext_x = surface.get_width() - tagtext_image.get_width() - 2
    tagtext_y = tagbg_y + tagbg_image.get_height() // 2 - tagtext_image.get_height() // 2
    surface.blit(tagtext_image, (tagtext_x, tagtext_y))

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

    CARD_MARGIN = 16
    CARD_SPACING = 2
    CARD_LIFT = 4
    card_width = assets.sprites["card_buy"].get_width()
    cards_x = surface.get_width() - (card_width + CARD_SPACING) * len(ctx.options) + CARD_SPACING - CARD_MARGIN
    cards_y = 96
    card_x = cards_x
    for i, option in enumerate(ctx.options):
      card_y = cards_y
      card_color = RED if option == "exit" else BLUE
      card_image = assets.sprites["card_" + option]
      card_image = replace_color(card_image, old_color=BLACK, new_color=card_color)
      if i == ctx.option_index:
        card_y -= CARD_LIFT
      else:
        card_image = darken(card_image)
      surface.blit(card_image, (card_x, card_y))
      card_x += card_image.get_width() + CARD_SPACING

    controls_x = surface.get_width() - 8
    controls_y = surface.get_height() - 12
    for control in ctx.controls:
      control_image = control.render()
      control_x = controls_x - control_image.get_width()
      control_y = controls_y - control_image.get_height() // 2
      surface.blit(control_image, (control_x, control_y))
      controls_x = control_x - 8
