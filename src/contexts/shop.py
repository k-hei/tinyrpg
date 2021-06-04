import pygame
from pygame import Rect
from contexts import Context
from contexts.sell import SellContext
from assets import load as use_assets
from filters import replace_color, darken
from palette import BLACK, WHITE, RED, BLUE

class ShopContext(Context):
  def __init__(ctx):
    super().__init__()
    ctx.option_index = 0
    ctx.options = ["buy", "sell", "exit"]

  def draw(ctx, surface):
    sprites = use_assets().sprites
    surface.fill(WHITE)
    pygame.draw.rect(surface, BLACK, Rect(0, 112, 256, 112))

    tagbg_image = sprites["shop_tag"]
    tagbg_x = surface.get_width() - tagbg_image.get_width()
    tagbg_y = 0
    surface.blit(tagbg_image, (tagbg_x, tagbg_y))

    tagtext_image = sprites["general_store"]
    tagtext_x = surface.get_width() - tagtext_image.get_width() - 2
    tagtext_y = tagbg_y + tagbg_image.get_height() // 2 - tagtext_image.get_height() // 2
    surface.blit(tagtext_image, (tagtext_x, tagtext_y))

    CARD_SPACING = 2
    CARD_LIFT = 4
    card_width = sprites["card_buy"].get_width()
    cards_x = surface.get_width() - (card_width + CARD_SPACING) * len(ctx.options)
    cards_y = 96
    card_x = cards_x
    for i, option in enumerate(ctx.options):
      card_y = cards_y
      card_color = RED if option == "exit" else BLUE
      card_image = sprites["card_" + option]
      card_image = replace_color(card_image, old_color=BLACK, new_color=card_color)
      if i == ctx.option_index:
        card_y -= CARD_LIFT
      else:
        card_image = darken(card_image)
      surface.blit(card_image, (card_x, card_y))
      card_x += card_image.get_width() + CARD_SPACING
