from math import sin, pi
import pygame
from pygame import Surface, Rect, SRCALPHA
from pygame.transform import flip
from contexts import Context
from comps.control import Control
from comps.card import Card
from comps.textbubble import TextBubble
from palette import BLACK, WHITE, GRAY, GRAY_DARK, BLUE, GOLD, CYAN
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
from savedata.resolve import resolve_material
from config import WINDOW_WIDTH, WINDOW_HEIGHT
from sprite import Sprite

class SelectAnim(TweenAnim): blocking = False
class DeselectAnim(TweenAnim): blocking = False
class CardAnim(TweenAnim): blocking = True

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
  MAX_VISIBLE_ITEMS = 4

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

  def render(bag, scroll=0, tab=None, selection=[]):
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
      track_width = 2
      track_height = bag.box.get_height() - 6 * 2
      track_x = bag.box.get_width() - track_width - 6
      track_y = 7
      pygame.draw.rect(bag.surface, GRAY_DARK, Rect(
        (track_x, track_y),
        (track_width, track_height)
      ))
      bar_height = BagList.MAX_VISIBLE_ITEMS / len(bag.items) * track_height
      if bar_height < track_height:
        scroll_max = max(0, len(bag.items) - BagList.MAX_VISIBLE_ITEMS)
        bar_y = min(1, scroll / (scroll_max or 1)) * (track_height - bar_height)
        pygame.draw.rect(bag.surface, WHITE, Rect(
          (track_x, track_y + bar_y),
          (track_width, bar_height)
        ))
      y += (round(scroll) - scroll) * 18
      for i in range(round(scroll), round(scroll) + BagList.MAX_VISIBLE_ITEMS):
        item = bag.items[i] if i < len(bag.items) else None
        item_anim = next((a for a in bag.anims if a.target == i), None)
        if item and (not item_anim or item_anim.time > 0):
          icon_image = item.render(item)

          name = item.name[:item_anim.time] if item_anim else item.name
          text_color = CYAN if (tab, i) in selection else WHITE
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

class SellContext(Context):
  class CursorAnim(Anim): blocking = False
  class DescAnim(Anim): blocking = False
  class DescEnterAnim(TweenAnim): blocking = True
  class ItemListAnim(TweenAnim): blocking = True
  class TagEnterAnim(TweenAnim): blocking = True
  class CardAnim(TweenAnim): blocking = True

  def __init__(ctx, items, bubble=None, portrait=None, card=None, on_close=None):
    super().__init__(on_close=on_close)
    ctx.items = items
    ctx.bubble = bubble or TextBubble(width=96, pos=(128, 40))
    ctx.portrait = portrait
    ctx.card = card or Card("sell")
    ctx.cursor = 0
    ctx.cursor_drawn = 0
    ctx.scroll = 0
    ctx.scroll_drawn = 0
    ctx.selection = []
    ctx.anims = []
    ctx.requires_release = {}
    ctx.hero = KnightCore()
    ctx.hud = Hud()
    ctx.tablist = BagTabs(Inventory.tabs)
    ctx.itembox = BagList((148, 76), items=filter_items(items, ctx.tablist.selection()))
    ctx.controls = [
      Control(key=("X"), value="Multi"),
      Control(key=("L", "R"), value="Tab")
    ]
    ctx.reset_cursor()

  def enter(ctx):
    ctx.anims.append(ctx.TagEnterAnim(duration=10, delay=25))
    ctx.anims.append(ctx.DescEnterAnim(duration=20, delay=25))
    ctx.anims.append(ctx.ItemListAnim(duration=20, delay=25))
    if ctx.card:
      # ctx.card.spin(duration=30)
      if ctx.card.sprite:
        ctx.anims.append(ctx.CardAnim(
          duration=30,
          delay=5,
          target=ctx.card.sprite.pos
        ))
    ctx.portrait.start_talk()
    ctx.bubble.print("MIRA: Got something to sell me?", on_end=ctx.portrait.stop_talk)

  def exit(ctx, on_end=None):
    ctx.close()

  def handle_keydown(ctx, key):
    if next((a for a in ctx.anims if a.blocking), None) or ctx.tablist.anims:
      return

    key_time = keyboard.get_pressed(key)
    if (key_time == 1
    or key_time > 30 and key_time % 2
    ):
      if key in (pygame.K_UP, pygame.K_w):
        return ctx.handle_move(-1)
      if key in (pygame.K_DOWN, pygame.K_s):
        return ctx.handle_move(1)
      if key in (pygame.K_LEFT, pygame.K_a):
        return ctx.handle_move(-5)
      if key in (pygame.K_RIGHT, pygame.K_d):
        return ctx.handle_move(5)
      if key == pygame.K_SPACE and not key in ctx.requires_release:
        control = next((c for c in ctx.controls if c.value == "Multi"), None)
        control.press("X")
        if not ctx.handle_select() or not ctx.handle_move(1):
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

    if key == pygame.K_BACKSPACE:
      return ctx.handle_clear()

    if key == pygame.K_ESCAPE:
      return ctx.handle_close()

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
    if abs(delta) == 1 or ctx.scroll + delta < 0:
      if ctx.cursor < ctx.scroll:
        ctx.scroll = ctx.cursor
      if ctx.cursor >= ctx.scroll + BagList.MAX_VISIBLE_ITEMS:
        ctx.scroll = ctx.cursor - BagList.MAX_VISIBLE_ITEMS + 1
    elif ctx.scroll + delta < max_index:
      ctx.scroll += delta
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
    ctx.scroll = 0
    ctx.scroll_drawn = 0
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

  def handle_clear(ctx):
    ctx.selection = []
    return True

  def handle_close(ctx):
    return ctx.exit(on_end=ctx.close)

  def reset_cursor(ctx):
    ctx.cursor = 0
    ctx.cursor_drawn = 0
    ctx.scroll = 0
    ctx.scroll_drawn = 0
    ctx.anims = [
      ctx.CursorAnim(),
      ctx.DescAnim()
    ]

  def update(ctx):
    for anim in ctx.anims:
      if anim.done:
        ctx.anims.remove(anim)
      else:
        anim.update()
    ctx.scroll_drawn += (ctx.scroll - ctx.scroll_drawn) / 4
    if ctx.cursor_drawn != None:
      ctx.cursor_drawn += (ctx.cursor - ctx.scroll - ctx.cursor_drawn) / 4

  def view(ctx):
    sprites = []
    assets = use_assets()

    MARGIN = 2

    tagtext_image = assets.sprites["fortune_house"]
    tag_image = assets.sprites["shop_tag"].copy()
    tag_image.blit(tagtext_image, (
      tag_image.get_width() - tagtext_image.get_width() - 2,
      2
    ))

    tag_x = WINDOW_WIDTH - tag_image.get_width()
    tag_y = 0
    tag_anim = next((a for a in ctx.anims if type(a) is SellContext.TagEnterAnim), None)
    if tag_anim:
      tag_y = lerp(-tag_image.get_height(), 0, tag_anim.pos)
    sprites.append(Sprite(
      image=tag_image,
      pos=(tag_x, tag_y)
    ))

    hud_image = ctx.hud.update(ctx.hero)
    hud_x = MARGIN
    hud_y = WINDOW_HEIGHT - hud_image.get_height() - MARGIN

    gold_image = assets.sprites["item_gold"]
    gold_image = replace_color(gold_image, BLACK, GOLD)
    gold_x = hud_x + hud_image.get_width() + 2
    gold_y = hud_y + hud_image.get_height() - gold_image.get_height() - 2
    sprites.append(Sprite(
      image=gold_image,
      pos=(gold_x, gold_y)
    ))

    goldtext_font = assets.ttf["roman"]
    goldtext_image = goldtext_font.render("500")
    goldtext_x = gold_x + gold_image.get_width() + 3
    goldtext_y = gold_y + gold_image.get_height() // 2 - goldtext_image.get_height() // 2
    sprites.append(Sprite(
      image=goldtext_image,
      pos=(goldtext_x, goldtext_y)
    ))

    surplus = 0
    for tab, i in ctx.selection:
      items = filter_items(ctx.items, tab)
      item = items[i]
      surplus += item.value // 2
    if surplus:
      surplus_image = goldtext_font.render("(+{})".format(surplus), CYAN)
      sprites.append(Sprite(
        image=surplus_image,
        pos=(
          goldtext_x + goldtext_image.get_width(),
          goldtext_y
        )
      ))
      select_image = goldtext_font.render("{count} item{s}".format(
        count=len(ctx.selection),
        s="s" if len(ctx.selection) != 1 else ""
      ), CYAN)
      sprites.append(Sprite(
        image=select_image,
        pos=(
          gold_x + 2,
          gold_y - select_image.get_height() - 1
        )
      ))

    controls_x = WINDOW_WIDTH - 8
    controls_y = WINDOW_HEIGHT - 12
    for control in ctx.controls:
      control_image = control.render()
      control_x = controls_x - control_image.get_width()
      control_y = controls_y - control_image.get_height() // 2
      sprites.append(Sprite(
        image=control_image,
        pos=(control_x, control_y)
      ))
      controls_x = control_x - 8

    tabs_image = ctx.tablist.render()
    items_image = ctx.itembox.render(
      scroll=ctx.scroll_drawn,
      tab=ctx.tablist.selection(),
      selection=ctx.selection
    )
    menu_x = WINDOW_WIDTH - items_image.get_width() - MARGIN
    menu_y = WINDOW_HEIGHT - items_image.get_height() - tabs_image.get_height() - 24
    menu_ytrue = menu_y
    menu_anim = next((a for a in ctx.anims if type(a) is ctx.ItemListAnim), None)
    if menu_anim:
      t = menu_anim.pos
      t = ease_out(t)
      menu_ytrue = lerp(WINDOW_HEIGHT, menu_y, t)
    sprites += [
      Sprite(
        image=tabs_image,
        pos=(menu_x, menu_ytrue)
      ),
      Sprite(
        image=items_image,
        pos=(menu_x, menu_ytrue + tabs_image.get_height())
      )
    ]

    descbox_width = WINDOW_WIDTH - items_image.get_width() - MARGIN * 3
    descbox_height = WINDOW_HEIGHT - menu_y - hud_image.get_height() - MARGIN * 2
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
            desc_y += desc_font.height() + 4
            continue
        char_image = assets.ttf["roman"].render(char)
        descbox_image.blit(char_image, (desc_x, desc_y))
        desc_x += char_image.get_width()
      label_text = (issubclass(item, MaterialItem)
        and "Via"
        or "No. owned")
      label_image = assets.ttf["english"].render(label_text)
      label_x = PADDING
      label_y = descbox_image.get_height() - label_image.get_height() - PADDING
      descbox_image.blit(label_image, (label_x, label_y))
      value = (issubclass(item, MaterialItem)
        and (resolve_material(item) and resolve_material(item).__name__ or "N/A")
        or len([i for i in ctx.itembox.items if i is item]))
      value_text = str(value)
      value_image = assets.ttf["roman"].render(value_text)
      descbox_image.blit(value_image, (label_x + label_image.get_width() + 5, label_y))

    descbox_anim = next((a for a in ctx.anims if type(a) is ctx.DescEnterAnim), None)
    descbox_x = MARGIN
    descbox_y = hud_y - MARGIN - descbox_height
    if descbox_anim:
      t = descbox_anim.pos
      t = ease_out(t)
      descbox_x = lerp(-descbox_image.get_width(), descbox_x, t)
    sprites.append(Sprite(
      image=descbox_image,
      pos=(descbox_x, descbox_y)
    ))

    card_image = assets.sprites["card_back"]
    card_x = menu_x + items_image.get_width() - card_image.get_width() // 2
    card_y = menu_y + tabs_image.get_height() - card_image.get_height() // 2 - 1
    card_anim = next((a for a in ctx.anims if type(a) is ctx.CardAnim), None)
    if card_anim:
      t = card_anim.pos
      t = ease_out(t)
      start_x, start_y = card_anim.target
      target_x, target_y = (card_x, card_y)
      card_x = lerp(start_x, target_x, t)
      card_y = lerp(start_y, target_y, t)
    card_sprite = ctx.card.render()
    card_sprite.pos = (card_x, card_y)
    sprites.append(card_sprite)

    if ctx.itembox.items and ctx.cursor_drawn != None and not next((a for a in ctx.anims if a.blocking), None):
      cursor_anim = next((a for a in ctx.anims if type(a) is ctx.CursorAnim), None)
      hand_color = CYAN if ctx.selection else BLACK
      hand_image = assets.sprites["hand"]
      hand_image = replace_color(hand_image, BLACK, hand_color)
      hand_image = flip(hand_image, True, False)
      hand_x = menu_x - 24
      if cursor_anim:
        hand_x += sin(cursor_anim.time % 30 / 30 * 2 * pi) * 2
      hand_y = menu_y + tabs_image.get_height() + 4
      hand_y += ctx.cursor_drawn * 18
      sprites.append(Sprite(
        image=hand_image,
        pos=(hand_x, hand_y)
      ))

    return sprites
