from math import sin, pi
import pygame
from pygame import Surface, Rect, SRCALPHA
from pygame.transform import flip
from contexts import Context
from palette import BLACK, WHITE, GRAY, GRAY_DARK, BLUE, GOLD
from filters import replace_color
from assets import load as use_assets
from inventory import Inventory
import keyboard
from cores.knight import KnightCore
from anims import Anim
from anims.tween import TweenAnim
from easing.expo import ease_out
from lib.lerp import lerp
from items.materials import MaterialItem
from hud import Hud

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
    tablist.on_anim = None
    tablist.surface = None

  def selection(tablist, index=None):
    if index is None:
      index = tablist.index
    return tablist.names[index]

  def _select(tablist, delta, on_end=None):
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
      duration=6,
      target=tablist.names[old_index]
    ))
    tablist.anims.append(SelectAnim(
      duration=8,
      target=tablist.names[new_index],
      on_end=on_end
    ))
    return tablist.names[new_index]

  def select_prev(tablist, on_end=None):
    return tablist._select(-1, on_end)

  def select_next(tablist, on_end=None):
    return tablist._select(1, on_end)

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
        tab_image.blit(part_image, (tab_width - part_width * 2 + 1, 0))
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

class BagList:
  def __init__(bag, size, items=None):
    bag.size = size
    bag.anims = []
    bag.surface = None
    bag.box = None
    bag.load(items or [])

  def load(bag, items):
    bag.items = items
    bag.anims = []
    if items:
      for i, item in enumerate(items):
        bag.anims.append(Anim(
          duration=len(item.name),
          delay=i * 2,
          target=i
        ))

  def update(bag):
    for anim in bag.anims:
      if anim.done:
        bag.anims.remove(anim)
      else:
        anim.update()

  def render(bag, tab=None, selection=[]):
    bag.update()
    assets = use_assets()
    x = 4
    y = 3
    if bag.box is None:
      bag.box = Box.render(bag.size)
    if bag.surface is None:
      bag.surface = Surface(bag.box.get_size())
    bag.surface.blit(bag.box, (0, 0))
    if bag.items == []:
      text_image = assets.ttf["roman"].render("[ No items ]")
      x = bag.box.get_width() // 2 - text_image.get_width() // 2
      y = bag.box.get_height() // 2 - text_image.get_height() // 2
      bag.surface.blit(text_image, (x, y))
    elif bag.items is not None:
      for i in range(min(5, len(bag.items))):
        item = bag.items[i]
        item_anim = next((a for a in bag.anims if a.target == i), None)
        if not item_anim or item_anim.time > 0:
          icon_image = item.render(item)

          name = item.name[:item_anim.time] if item_anim else item.name
          text_color = GOLD if (tab, i) in selection else WHITE
          text_image = assets.ttf["english"].render(name, text_color)
          bag.surface.blit(icon_image, (x, y))

          text_x = x + icon_image.get_width() + 4
          text_y = y + icon_image.get_height() // 2 - text_image.get_height() // 2
          bag.surface.blit(text_image, (text_x, text_y))

          price_image = assets.ttf["roman"].render(str(item.value // 2), text_color)
          price_x = bag.box.get_width() - price_image.get_width() - 12
          price_y = text_y
          bag.surface.blit(price_image, (price_x, price_y))

          coin_image = assets.sprites["coin"]
          coin_image = replace_color(coin_image, BLACK, GOLD)
          coin_x = price_x - coin_image.get_width() - 3
          coin_y = y + icon_image.get_height() // 2 - coin_image.get_height() // 2 - 1
          bag.surface.blit(coin_image, (coin_x, coin_y))

        pygame.draw.rect(bag.surface, GRAY_DARK, Rect(
          (x + 16 + 4, y + 15),
          (bag.box.get_width() - x - 32, 1)
        ))
        y += 16 + 2
    return bag.surface

class Control:
  def __init__(control, key, value):
    control.key = key
    control.value = value
    control.surface = None
    control.dirty = True
    control.pressed = {}
    for key in control.key:
      control.pressed[key] = False

  def press(control, key):
    if not control.pressed[key]:
      control.pressed[key] = True
      control.dirty = True

  def release(control, key):
    if control.pressed[key]:
      control.pressed[key] = False
      control.dirty = True

  def render(control):
    if control.surface and not control.dirty:
      return control.surface
    assets = use_assets()
    font = assets.ttf["roman"]
    nodes = []
    x = 0
    for key in control.key:
      icon_color = GOLD if control.pressed[key] else BLUE
      icon_image = assets.sprites["button_" + key.lower()]
      icon_image = replace_color(icon_image, BLACK, icon_color)
      nodes.append((icon_image, x))
      x += icon_image.get_width() + 2
    x += 2
    text_image = font.render(control.value)
    nodes.append((text_image, x))
    surface_width = x + text_image.get_width()
    surface_height = icon_image.get_height()
    if control.surface is None:
      control.surface = Surface((surface_width, surface_height), SRCALPHA)
    else:
      control.surface.fill(0)
    for image, x in nodes:
      y = surface_height // 2 - image.get_height() // 2
      control.surface.blit(image, (x, y))
    return control.surface

class TextBox:
  def __init__(box, size):
    box.size = size

class SellContext(Context):
  class CursorAnim(Anim): blocking = False
  class DescAnim(Anim): blocking = False

  def __init__(ctx, items):
    super().__init__()
    ctx.items = items
    ctx.cursor = 0
    ctx.cursor_drawn = 0
    ctx.selection = []
    ctx.anims = []
    ctx.requires_release = {}
    ctx.hero = KnightCore()
    ctx.hud = Hud()
    ctx.tablist = BagTabs(Inventory.tabs)
    ctx.itembox = BagList((148, 96), items=filter_items(items, ctx.tablist.selection()))
    ctx.controls = [
      Control(key=("X"), value="Multi"),
      Control(key=("L", "R"), value="Tab")
    ]
    ctx.reset_cursor()

  def handle_keydown(ctx, key):
    if next((a for a in ctx.anims if a.blocking), None) or ctx.tablist.anims:
      return

    key_time = keyboard.get_pressed(key)
    if (key_time == 1
    or key_time > 30 and key_time % 2
    ):
      if key == pygame.K_UP:
        return ctx.handle_move(-1)
      if key == pygame.K_DOWN:
        return ctx.handle_move(1)
      if key == pygame.K_SPACE and not key in ctx.requires_release:
        control = next((c for c in ctx.controls if c.value == "Multi"), None)
        control.press("X")
        ctx.handle_select()
        if not ctx.handle_move(1):
          ctx.requires_release[key] = True
        return True

    if key_time > 1:
      return

    if key == pygame.K_TAB:
      control = next((c for c in ctx.controls if c.value == "Tab"), None)
      if (keyboard.get_pressed(pygame.K_LSHIFT)
      or keyboard.get_pressed(pygame.K_RSHIFT)):
        control.press("L")
        return ctx.handle_tab(delta=-1)
      else:
        control.press("R")
        return ctx.handle_tab(delta=1)

  def handle_keyup(ctx, key):
    if key == pygame.K_TAB:
      control = next((c for c in ctx.controls if c.value == "Tab"), None)
      control.release("L")
      control.release("R")
    elif key == pygame.K_SPACE:
      control = next((c for c in ctx.controls if c.value == "Multi"), None)
      control.release("X")
      if key in ctx.requires_release:
        del ctx.requires_release[key]

  def handle_move(ctx, delta):
    old_index = ctx.cursor
    new_index = old_index + delta
    min_index = 0
    max_index = len(ctx.itembox.items) - 1
    if new_index < min_index:
      new_index = min_index
    if new_index > max_index:
      new_index = max_index
    if new_index == old_index:
      return False
    ctx.cursor = new_index
    next((a for a in ctx.anims if type(a) is ctx.DescAnim), None).time = 0
    return True

  def handle_tab(ctx, delta=1):
    if delta == -1:
      tab = ctx.tablist.select_prev(on_end=ctx.reset_cursor)
    elif delta == 1:
      tab = ctx.tablist.select_next(on_end=ctx.reset_cursor)
    else:
      return False
    items = filter_items(ctx.items, tab)
    ctx.itembox.load(items)
    ctx.cursor = 0
    ctx.cursor_drawn = None
    ctx.anims = []
    return True

  def handle_select(ctx):
    if not ctx.itembox.items:
      return False
    node = (ctx.tablist.selection(), ctx.cursor)
    if node in ctx.selection:
      ctx.selection.remove(node)
      return False
    else:
      ctx.selection.append(node)
      return True

  def reset_cursor(ctx):
    ctx.cursor = 0
    ctx.cursor_drawn = 0
    ctx.anims = [
      ctx.CursorAnim(),
      ctx.DescAnim()
    ]

  def update(ctx):
    for anim in ctx.anims:
      anim.update()
    if ctx.cursor_drawn != None:
      ctx.cursor_drawn += (ctx.cursor - ctx.cursor_drawn) / 4

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
    tagtext_x = surface.get_width() - tagtext_image.get_width() - MARGIN
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

    surplus = 0
    for tab, i in ctx.selection:
      items = filter_items(ctx.items, tab)
      item = items[i]
      surplus += item.value // 2
    if surplus:
      surplus_image = goldtext_font.render("(+{})".format(surplus), GOLD)
      surface.blit(surplus_image, (goldtext_x + goldtext_image.get_width(), goldtext_y))
      select_image = goldtext_font.render("{count} item{s}".format(
        count=len(ctx.selection),
        s="s" if len(ctx.selection) != 1 else ""
      ), GOLD)
      surface.blit(select_image, (gold_x + 2, gold_y - select_image.get_height() - 1))

    tabs_image = ctx.tablist.render()
    items_image = ctx.itembox.render(ctx.tablist.selection(), ctx.selection)
    menu_x = surface.get_width() - items_image.get_width() - MARGIN
    menu_y = surface.get_height() - items_image.get_height() - tabs_image.get_height() - 24
    surface.blit(tabs_image, (menu_x, menu_y))
    surface.blit(items_image, (menu_x, menu_y + tabs_image.get_height()))

    card_image = assets.sprites["card_sell"]
    card_image = replace_color(card_image, BLACK, BLUE)
    card_x = menu_x + items_image.get_width() - card_image.get_width()
    card_y = menu_y - card_image.get_height() + tabs_image.get_height() - 1
    surface.blit(card_image, (card_x, card_y))

    descbox_width = surface.get_width() - items_image.get_width() - MARGIN * 3
    descbox_height = surface.get_height() - menu_y - tabs_image.get_height() - hud_image.get_height() - MARGIN * 2
    descbox_image = Box.render((descbox_width, descbox_height))
    item = ctx.itembox.items and ctx.itembox.items[ctx.cursor]
    desc_anim = next((a for a in ctx.anims if type(a) is ctx.DescAnim), None)
    if item and desc_anim:
      title_image = assets.ttf["english"].render(item.name, item.color)
      PADDING = 8
      descbox_image.blit(title_image, (PADDING, PADDING))
      desc_font = assets.ttf["roman"]
      desc_x = PADDING
      desc_y = 21
      desc_right = descbox_image.get_width() - PADDING
      prev_space = 0
      for i, char in enumerate(item.desc[:desc_anim.time]):
        if prev_space == 0 or char in (" ", "\n"):
          prev_space = i + 1
          next_space = item.desc.find(" ", prev_space)
          if next_space == -1:
            next_space = item.desc.find("\n", prev_space)
          if next_space == -1:
            next_space = len(item.desc)
          word = item.desc[prev_space:next_space]
          if char == "\n" or desc_x + desc_font.width(word) > desc_right:
            desc_x = PADDING
            desc_y += desc_font.height() + 3
            continue
        char_image = assets.ttf["roman"].render(char)
        descbox_image.blit(char_image, (desc_x, desc_y))
        desc_x += char_image.get_width()
      count_image = assets.ttf["english"].render("No. owned")
      count_x = PADDING
      count_y = descbox_image.get_height() - count_image.get_height() - PADDING
      descbox_image.blit(count_image, (count_x, count_y))
      value = len([i for i in ctx.itembox.items if i is item])
      value_image = assets.ttf["roman"].render(str(value))
      descbox_image.blit(value_image, (count_x + count_image.get_width() + 6, count_y))

    descbox_x = MARGIN
    descbox_y = hud_y - MARGIN - descbox_height
    surface.blit(descbox_image, (descbox_x, descbox_y))

    if ctx.itembox.items and ctx.cursor_drawn != None:
      cursor_anim = next((a for a in ctx.anims if type(a) is ctx.CursorAnim), None)
      hand_image = assets.sprites["hand"]
      hand_image = replace_color(hand_image, BLACK, BLUE)
      hand_image = flip(hand_image, True, False)
      hand_x = menu_x - 24
      if cursor_anim:
        hand_x += sin(cursor_anim.time % 30 / 30 * 2 * pi) * 2
      hand_y = menu_y + tabs_image.get_height() + 4
      hand_y += ctx.cursor_drawn * 18
      surface.blit(hand_image, (hand_x, hand_y))

    controls_x = surface.get_width() - 8
    controls_y = surface.get_height() - 12
    for control in ctx.controls:
      control_image = control.render()
      control_x = controls_x - control_image.get_width()
      control_y = controls_y - control_image.get_height() // 2
      surface.blit(control_image, (control_x, control_y))
      controls_x = control_x - 8
