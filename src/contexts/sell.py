from contexts import Context
import pygame
from pygame import Surface, SRCALPHA
from palette import BLACK, WHITE, GRAY
from filters import replace_color
from assets import load as use_assets
from inventory import Inventory
import keyboard

class Box:
  TILE_SIZE = 8

  def render(size):
    sprites = use_assets().sprites
    surface = Surface(size)
    surface.fill(BLACK)
    width, height = size
    cols = width // Box.TILE_SIZE
    rows = height // Box.TILE_SIZE
    for row in range(rows):
      surface.blit(sprites["item_tile_w"], (0, row * Box.TILE_SIZE))
      surface.blit(sprites["item_tile_e"], (width - Box.TILE_SIZE, row * Box.TILE_SIZE))
    surface.blit(sprites["item_tile_nw"], (0, 0))
    surface.blit(sprites["item_tile_sw"], (0, height - Box.TILE_SIZE))
    surface.blit(sprites["item_tile_ne"], (width - Box.TILE_SIZE, 0))
    surface.blit(sprites["item_tile_se"], (width - Box.TILE_SIZE, height - Box.TILE_SIZE))
    return surface

  def __init__(box, size):
    box.size = size

class SellContext(Context):
  def __init__(ctx, items):
    super().__init__()
    ctx.items = items
    ctx.tab = 0
    ctx.cursor = 0
    ctx.cache_box = None

  def init(ctx):
    ctx.cache_box = Box.render((128, 96))

  def handle_keydown(ctx, key):
    if keyboard.get_pressed(key) > 1:
      return

    if key == pygame.K_TAB:
      ctx.handle_tab()

  def handle_tab(ctx):
    ctx.tab = (ctx.tab + 1) % len(Inventory.tabs)

  def draw(ctx, surface):
    sprites = use_assets().sprites
    surface.fill(WHITE)
    x = 0
    for i, tab in enumerate(Inventory.tabs):
      icon_image = sprites["icon_" + tab]
      text_image = sprites[tab]
      if i == ctx.tab:
        inner_width = icon_image.get_width() + 3 + text_image.get_width()
        tab_width = inner_width + 9
        tab_image = Surface((tab_width, 16), SRCALPHA)
        part_image = sprites["item_tab_m"]
        part_width = part_image.get_width()
        for j in range(tab_width // part_width - 1):
          tab_image.blit(part_image, (part_width * (j + 1), 0))
        tab_image.blit(sprites["item_tab_l"], (0, 0))
        tab_image.blit(sprites["item_tab_r"], (tab_width - part_width, 0))
      else:
        inner_width = icon_image.get_width()
        tab_image = sprites["item_tab"].copy()
      tab_image.blit(icon_image, (4, 5))
      if i == ctx.tab:
        tab_image.blit(text_image, (4 + icon_image.get_width() + 3, 6))
      else:
        tab_image = replace_color(tab_image, WHITE, GRAY)
      surface.blit(tab_image, (x, 0))
      x += tab_image.get_width() + 1
    surface.blit(ctx.cache_box, (0, 16))
