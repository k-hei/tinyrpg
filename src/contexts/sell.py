from contexts import Context
import pygame
from pygame import Surface, Rect, SRCALPHA
from palette import BLACK, WHITE, GRAY, GRAY_DARK, GOLD
from filters import replace_color
from assets import load as use_assets
from inventory import Inventory
import keyboard
from anims.tween import TweenAnim
from easing.expo import ease_out
from lib.lerp import lerp
from items.materials import MaterialItem

class SelectAnim(TweenAnim): blocking = False
class DeselectAnim(TweenAnim): blocking = False

def filter_items(items, tab):
  return list(filter(lambda item: (
    tab == "consumables" and not issubclass(item, MaterialItem)
    or tab == "materials" and issubclass(item, MaterialItem)
    or tab == "equipment" and False
  ), items))

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

class BagTabs:
  def __init__(tablist, names):
    tablist.names = names
    tablist.index = 0
    tablist.anims = []
    tablist.surface = None

  def _select(tablist, delta):
    old_index = tablist.index
    new_index = old_index + delta
    if new_index >= len(tablist.names):
      new_index = 0
    elif new_index < 0:
      new_index = len(tablist.names) - 1
    if new_index == old_index:
      return tablist.names[old_index]
    tablist.index = new_index
    tablist.anims.append(DeselectAnim(
      duration=8,
      target=tablist.names[old_index]
    ))
    tablist.anims.append(SelectAnim(
      duration=8,
      target=tablist.names[new_index]
    ))
    return tablist.names[new_index]

  def select_prev(tablist):
    tablist._select(-1)

  def select_next(tablist):
    tablist._select(1)

  def update(tablist):
    if tablist.anims:
      anim = tablist.anims[0]
      if anim.done:
        tablist.anims.pop(0)
      else:
        anim.update()

  def render(tablist):
    tablist.update()
    sprites = use_assets().sprites
    nodes = []
    x = 0
    for i, tab in enumerate(Inventory.tabs):
      icon_image = sprites["icon_" + tab]
      tab_anim = next((a for a in tablist.anims if a.target == tab), None)
      if i == tablist.index or tab_anim:
        text_image = sprites[tab]
        min_width = icon_image.get_width()
        max_width = icon_image.get_width() + 3 + text_image.get_width()
        if tab_anim:
          t = ease_out(tab_anim.pos)
          if type(tab_anim) is DeselectAnim:
            inner_width = lerp(max_width, min_width, t)
          elif type(tab_anim) is SelectAnim:
            inner_width = lerp(min_width, max_width, t)
        else:
          inner_width = max_width
        tab_width = int(inner_width) + 9
        tab_image = Surface((tab_width, 16), SRCALPHA)
        part_image = sprites["item_tab_m"]
        part_width = part_image.get_width()
        for j in range(tab_width // part_width - 2):
          tab_image.blit(part_image, (part_width * (j + 1), 0))
        tab_image.blit(part_image, (tab_width - part_width * 2, 0))
        tab_image.blit(sprites["item_tab_l"], (0, 0))
        tab_image.blit(sprites["item_tab_r"], (tab_width - part_width, 0))
      else:
        tab_image = sprites["item_tab"].copy()
      tab_image.blit(icon_image, (4, 5))
      if i == tablist.index:
        tab_image.blit(text_image, (4 + icon_image.get_width() + 3, 6))
      else:
        tab_image = replace_color(tab_image, WHITE, GRAY)
      nodes.append((tab_image, x))
      x += tab_image.get_width() + 1
    tab_image, x = nodes[-1]
    tabs_width = x + tab_image.get_width()
    if tablist.surface is None or tabs_width > tablist.surface.get_width():
      tablist.surface = Surface((tabs_width, tab_image.get_height()), SRCALPHA)
    else:
      tablist.surface.fill(0)
    for tab_image, x in nodes:
      tablist.surface.blit(tab_image, (x, 0))
    return tablist.surface

class SellContext(Context):
  def __init__(ctx, items):
    super().__init__()
    ctx.items = items
    ctx.cursor = 0
    ctx.cache_box = None
    ctx.tabs = BagTabs(Inventory.tabs)

  def init(ctx):
    ctx.cache_box = Box.render((160, 96))

  def handle_keydown(ctx, key):
    if keyboard.get_pressed(key) > 1:
      return

    if key == pygame.K_TAB:
      if (keyboard.get_pressed(pygame.K_LSHIFT)
      or keyboard.get_pressed(pygame.K_RSHIFT)):
        return ctx.tabs.select_prev()
      else:
        return ctx.tabs.select_next()

  def draw(ctx, surface):
    assets = use_assets()
    sprites = assets.sprites
    surface.fill(WHITE)

    surface.blit(ctx.tabs.render(), (0, 0))
    surface.blit(ctx.cache_box, (0, 16))

    x = 8
    y = 19
    items = filter_items(ctx.items, Inventory.tabs[ctx.tabs.index])
    if items:
      for i in range(5):
        if i < len(items):
          item = items[i]
          icon_image = item.render(item)
          text_image = assets.ttf["english"].render(item.name)
          surface.blit(icon_image, (x, y))

          text_x = x + icon_image.get_width() + 4
          text_y = y + icon_image.get_height() // 2 - text_image.get_height() // 2
          surface.blit(text_image, (text_x, text_y))

          price_image = assets.ttf["roman"].render(str(item.value // 2))
          price_x = ctx.cache_box.get_width() - price_image.get_width() - 12
          price_y = text_y
          surface.blit(price_image, (price_x, price_y))

          coin_image = sprites["coin"]
          coin_image = replace_color(coin_image, BLACK, GOLD)
          coin_x = price_x - coin_image.get_width() - 3
          coin_y = y + icon_image.get_height() // 2 - coin_image.get_height() // 2 - 1
          surface.blit(coin_image, (coin_x, coin_y))

        pygame.draw.rect(surface, GRAY_DARK, Rect(
          (x + 16 + 4, y + 15),
          (ctx.cache_box.get_width() - x - 32, 1)
        ))
        y += 16 + 2
    else:
      text_image = assets.ttf["roman"].render("[ No items ]")
      x = ctx.cache_box.get_width() // 2 - text_image.get_width() // 2
      y = 16 + ctx.cache_box.get_height() // 2 - text_image.get_height() // 2
      surface.blit(text_image, (x, y))
