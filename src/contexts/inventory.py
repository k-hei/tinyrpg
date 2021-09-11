import random
import pygame
from pygame import Surface, Rect, SRCALPHA
from pygame.transform import rotate

from contexts import Context
from contexts.choice import ChoiceContext, Choice
from comps.hud import Hud
from comps.invdesc import InventoryDescription
from comps.control import Control
from assets import load as use_assets
from filters import replace_color
import lib.gamepad as gamepad
import lib.keyboard as keyboard
from lib.keyboard import key_times, ARROW_DELTAS
from colors.palette import BLACK, WHITE, GRAY, BLUE, GOLD
from sprite import Sprite
from config import WINDOW_WIDTH, WINDOW_HEIGHT, INVENTORY_COLS, INVENTORY_ROWS

from anims.tween import TweenAnim
from anims.sine import SineAnim
from easing.expo import ease_out
from lib.lerp import lerp

from items.materials import MaterialItem

SPACING = 4
MARGIN = 8
DESC_PADDING_X = 12
DESC_PADDING_Y = 10
DESC_TITLE_SPACING = 5
DESC_WORD_SPACING = 8
DESC_LINE_SPACING = 3
ENTER_DURATION = 8
ENTER_STAGGER = 3
EXIT_DURATION = 4
EXIT_STAGGER = 2
DURATION_BELTENTER = 15
DURATION_BELTEXIT = 7
STAGGER_BELTEXIT = 0
DURATION_DESCENTER = 15
DURATION_DESCEXIT = 7
DURATION_CHARENTER = ENTER_DURATION
STAGGER_CHARENTER = 4
DURATION_CHAREXIT = 6
STAGGER_CHAREXIT = 2
BANNER_ENTER_DURATION = 7
BANNER_ENTER_DELAY = 30
BANNER_EXIT_DURATION = 7

class SelectAnim(TweenAnim): blocking = False
class DeselectAnim(TweenAnim): blocking = False

class InventoryContext(Context):
  tabs = ["consumables", "materials", "equipment"]

  def filter_items(items, tab):
    materials = [i for i in items if isinstance(i, MaterialItem) or type(i) is type and issubclass(i, MaterialItem)]
    if tab == "consumables":
      return [i for i in items if i not in materials]
    elif tab == "materials":
      return materials
    else:
      return []

  def __init__(ctx, store, on_close=None):
    super().__init__(on_close=on_close)
    ctx.store = store
    ctx.on_animate = None
    ctx.tab = 0
    ctx.cursor = (0, 0)
    ctx.cursor_anim = SineAnim(period=30)
    ctx.selection = None
    ctx.active = True
    ctx.anims = []
    ctx.box = InventoryDescription()
    ctx.grid_size = (INVENTORY_COLS, INVENTORY_ROWS)
    ctx.items = []
    ctx.controls = [
      Control(key=("X"), value="Arrange"),
      Control(key=("Y"), value="Sort"),
      Control(key=("L", "R"), value="Tab")
    ]
    ctx.update_items()

  def enter(ctx, on_end=None):
    ctx.describe_item()
    ctx.active = True
    ctx.box.enter()
    ctx.anims.append(TweenAnim(duration=DURATION_BELTENTER, target="belt"))
    for i, char in enumerate("item"):
      ctx.anims.append(TweenAnim(
        duration=DURATION_CHARENTER,
        delay=STAGGER_CHARENTER * (i + 1),
        target=char
      ))
    cols, rows = ctx.grid_size
    for row in range(rows):
      for col in range(cols):
        index = col * rows + row
        ctx.anims.append(TweenAnim(
          duration=ENTER_DURATION,
          delay=ENTER_STAGGER * index,
          target=(col, row)
        ))
    ctx.anims.append(TweenAnim(
      duration=ENTER_DURATION,
      delay=ENTER_STAGGER * (index + 1),
      target=(col + 1, row)
    ))
    for i, tab in enumerate(ctx.tabs):
      if i == ctx.tab:
        duration = 15
      else:
        duration = 10
      ctx.anims.append(TweenAnim(
        duration=duration,
        delay=rows * ENTER_STAGGER + i * 8,
        target=tab
      ))
    ctx.anims.append(TweenAnim(duration=BANNER_ENTER_DURATION, delay=BANNER_ENTER_DELAY, target="controls"))

  def exit(ctx):
    ctx.active = False
    ctx.box.exit()
    if ctx.child:
      ctx.child.exit()
    ctx.anims.append(TweenAnim(
      duration=DURATION_BELTEXIT,
      delay=STAGGER_BELTEXIT + STAGGER_CHAREXIT * 2,
      target="belt"
    ))
    ctx.anims.append(TweenAnim(duration=DURATION_DESCEXIT, target="desc"))
    for i, char in enumerate("item"):
      ctx.anims.append(TweenAnim(
        duration=DURATION_CHAREXIT,
        delay=STAGGER_BELTEXIT + STAGGER_CHAREXIT * i + 5,
        target=char
      ))
    cols, rows = ctx.grid_size
    for row in range(rows):
      for col in range(cols):
        index = cols * rows - (col * rows + row)
        ctx.anims.append(TweenAnim(
          duration=EXIT_DURATION,
          delay=EXIT_STAGGER * index,
          target=(col, row)
        ))
    ctx.anims.append(TweenAnim(
      duration=EXIT_DURATION,
      delay=EXIT_STAGGER * (index + 1),
      target=(col + 1, row)
    ))
    for i, tab in enumerate(ctx.tabs):
      if i == ctx.tab:
        duration = 8
      else:
        duration = 6
      ctx.anims.append(TweenAnim(
        duration=duration,
        delay=i * 4,
        target=tab
      ))
    ctx.anims.append(TweenAnim(duration=BANNER_EXIT_DURATION, target="controls"))

  def remove_anim(ctx, anim):
    if anim in ctx.anims:
      ctx.anims.remove(anim)
    if not ctx.anims and ctx.on_animate:
      ctx.on_animate()

  def find_extra_slot(ctx):
    return (ctx.grid_size[0], ctx.grid_size[1] - 1)

  def get_item_at(ctx, cell):
    cols, rows = ctx.grid_size
    col, row = cell
    index = row * cols + col
    if cell == ctx.find_extra_slot() and ctx.get_hero():
      return ctx.store.place.hero.item
    if index >= len(ctx.items) or not ctx.contains(cell):
      return None
    return ctx.items[index]

  def get_selected_item(ctx):
    return ctx.get_item_at(ctx.cursor)

  def describe_item(ctx, item=None):
    if item is None:
      item = ctx.get_item_at(ctx.cursor)
    if item:
      ctx.box.print(item)
    else:
      ctx.box.print("You have no items in this category.")

  def contains(ctx, cell):
    cols, rows = ctx.grid_size
    col, row = cell
    return col >= 0 and col < cols and row >= 0 and row < rows

  def handle_press(ctx, button):
    if next((a for a in ctx.anims if a.blocking), None):
      return False

    if ctx.child:
      return ctx.child.handle_press(button)

    if keyboard.get_pressed(button) + gamepad.get_state(button) > 1:
      return False

    if button in ARROW_DELTAS:
      delta = ARROW_DELTAS[button]
      return ctx.handle_move(delta)

    if button in (pygame.K_SPACE, gamepad.controls.manage):
      arrange_control = next((c for c in ctx.controls if c.value == "Arrange"), None)
      arrange_control.press()
      return ctx.handle_select()

    tab_control = next((c for c in ctx.controls if c.value == "Tab"), None)
    sort_control = next((c for c in ctx.controls if c.value == "Sort"), None)
    if ctx.selection:
      tab_control.disable()
      sort_control.disable()
      if button in (pygame.K_BACKSPACE, pygame.K_ESCAPE, gamepad.controls.cancel):
        return ctx.handle_select()
    else:
      tab_control.enable()
      sort_control.enable()
      if button == gamepad.L:
        tab_control.press("L")
        return ctx.handle_tab(delta=-1)
      elif button == gamepad.R:
        tab_control.press("R")
        return ctx.handle_tab(delta=1)

      if button == pygame.K_TAB:
        if (keyboard.get_pressed(pygame.K_LSHIFT)
        or keyboard.get_pressed(pygame.K_RSHIFT)
        ):
          tab_control.press("L")
          return ctx.handle_tab(delta=-1)
        else:
          tab_control.press("R")
          return ctx.handle_tab(delta=1)

      if button in (pygame.K_BACKSLASH, pygame.K_BACKQUOTE, gamepad.controls.item):
        sort_control.press()
        return ctx.handle_sort()

      if button in (pygame.K_RETURN, gamepad.controls.confirm):
        return ctx.handle_menu()

      if button in (pygame.K_BACKSPACE, pygame.K_ESCAPE, gamepad.controls.cancel):
        return ctx.exit()

  def handle_release(ctx, button):
    if button in (pygame.K_SPACE, gamepad.controls.manage):
      arrange_control = next((c for c in ctx.controls if c.value == "Arrange"), None)
      arrange_control.release()
      return

    if button in (pygame.K_BACKSLASH, pygame.K_BACKQUOTE, gamepad.controls.item):
      sort_control = next((c for c in ctx.controls if c.value == "Sort"), None)
      sort_control.release()
      return

    tab_control = next((c for c in ctx.controls if c.value == "Tab"), None)
    if button == pygame.K_TAB:
      tab_control.release("L")
      tab_control.release("R")
      return

    if button == gamepad.L:
      tab_control.release("L")
      return

    if button == gamepad.R:
      tab_control.release("R")
      return

  def handle_move(ctx, delta):
    delta_x, delta_y = delta
    cursor_x, cursor_y = ctx.cursor
    target_cell = (cursor_x + delta_x, cursor_y + delta_y)
    if not ctx.contains(target_cell) and target_cell != ctx.find_extra_slot():
      return False
    target_item = ctx.get_item_at(target_cell)
    ctx.cursor = target_cell
    if target_item and not ctx.selection:
      ctx.describe_item(target_item)

  def handle_tab(ctx, delta=1):
    old_tab = ctx.tab
    new_tab = old_tab + delta
    if new_tab < 0:
      new_tab = len(ctx.tabs) - 1
    elif new_tab >= len(ctx.tabs):
      new_tab = 0
    if old_tab != new_tab:
      ctx.tab = new_tab
      ctx.update_items()
      ctx.anims.append(DeselectAnim(
        duration=12,
        target=ctx.tabs[old_tab]
      ))
      ctx.anims.append(SelectAnim(
        duration=8,
        target=ctx.tabs[new_tab]
      ))
      cols, _ = ctx.grid_size
      for i, item in enumerate(ctx.items):
        ctx.anims.append(SelectAnim(
          duration=4,
          delay=i,
          target=(i % cols, i // cols)
        ))

  def update_items(ctx):
    ctx.items = InventoryContext.filter_items(ctx.store.items, ctx.tabs[ctx.tab])
    ctx.cursor = (0, 0)
    ctx.describe_item()

  def get_hero(ctx):
    return type(ctx.store.place).__name__.startswith("Dungeon") and ctx.store.place.hero

  def handle_menu(ctx):
    if ctx.get_item_at(ctx.cursor) is None:
      return False
    ctx.open(ChoiceContext(choices=[
      Choice(text="Use"),
      Choice(text="Carry", disabled=lambda: ctx.cursor == ctx.find_extra_slot()),
      Choice(text="Drop", closing=True)
    ], on_choose=lambda choice: (
      choice.text == "Use" and ctx.use_item()
      or choice.text == "Carry" and ctx.carry_item()
      or choice.text == "Drop" and ctx.drop_item()
    )))
    return True

  def map_cell_to_store(ctx, cell):
    cols, rows = ctx.grid_size
    col, row = cell
    index = row * cols + col
    item = ctx.items[index] if index < len(ctx.items) else None
    if not item:
      return -1
    tab_index = next((j for j, (i, _) in enumerate([(i, x) for i, x in enumerate(ctx.items) if x is item]) if i == index), None)
    store_index = [(i, x) for i, x in enumerate(ctx.store.items) if x is item][tab_index][0]
    return store_index

  def handle_select(ctx):
    if ctx.selection:
      hero = ctx.get_hero()
      if ctx.cursor != ctx.selection and ctx.selection == ctx.find_extra_slot() and hero:
        # swap from extra slot to inventory
        cursor_index = ctx.map_cell_to_store(ctx.cursor)
        old_item = ctx.get_item_at(ctx.cursor)
        if old_item:
          ctx.store.items[cursor_index] = hero.item
          hero.item = old_item
        else:
          ctx.store.items.append(hero.item)
          hero.item = None
      elif ctx.cursor != ctx.selection and ctx.cursor == ctx.find_extra_slot() and hero:
        # swap from inventory to extra slot
        selection_index = ctx.map_cell_to_store(ctx.selection)
        old_item = ctx.get_item_at(ctx.cursor)
        hero.item = ctx.store.items.pop(selection_index)
        if old_item:
          ctx.store.items.insert(selection_index, old_item)
      else:
        a = ctx.map_cell_to_store(ctx.selection)
        b = ctx.map_cell_to_store(ctx.cursor)
        if b == -1:
          ctx.store.items.append(ctx.store.items.pop(a))
        elif a != -1:
          ctx.store.items[a], ctx.store.items[b] = ctx.store.items[b], ctx.store.items[a]

      ctx.items = InventoryContext.filter_items(ctx.store.items, ctx.tabs[ctx.tab])
      ctx.selection = None
    else:
      if ctx.get_item_at(ctx.cursor) is None:
        return False
      ctx.selection = ctx.cursor

  def handle_sort(ctx):
    ITEM_ORDER = ["HpItem", "SpItem", "AilmentItem", "DungeonItem"]
    ctx.store.items = sorted(ctx.store.items, key=lambda item: (
      ITEM_ORDER.index(item.__bases__[0].__name__) * 255 * 26
      + (255 - item.color[0]) * 26
      + ord(item.__name__[0])
    ))
    ctx.items = InventoryContext.filter_items(ctx.store.items, ctx.tabs[ctx.tab])

  def use_item(ctx, item=None):
    item = item or ctx.get_selected_item()
    is_using_from_extra_slot = ctx.cursor == ctx.find_extra_slot()
    if "use_item" in dir(ctx.parent):
      success, message = ctx.parent.use_item(item, discard=not is_using_from_extra_slot)
    else:
      success, message = ctx.parent.store.use_item(item, discard=not is_using_from_extra_slot)
    if success:
      if is_using_from_extra_slot and ctx.get_hero():
        ctx.get_hero().item = None
      ctx.exit()
      return True
    else:
      ctx.box.print(message)
      return False

  def carry_item(ctx, item=None):
    item = item or ctx.get_selected_item()
    if ctx.cursor == ctx.find_extra_slot():
      success, message = False, "You're already carrying this!"
    elif "carry_item" in dir(ctx.parent):
      success, message = ctx.parent.carry_item(item)
    else:
      success, message = False, "You can't carry that here!"
    if success:
      ctx.store.discard_item(item)
      ctx.exit()
      return True
    else:
      ctx.box.print(message)
      return False

  def drop_item(ctx, item=None):
    item = item or ctx.get_selected_item()
    if "drop_item" in dir(ctx.parent):
      success, message = ctx.parent.drop_item(item)
    else:
      success, message = False, "You can't drop that here!"
    if success:
      if ctx.cursor == ctx.find_extra_slot() and ctx.get_hero():
        ctx.get_hero().item = None
      else:
        ctx.store.discard_item(item)
      ctx.exit()
      return True
    else:
      ctx.box.print(message)
      return False

  def update(ctx):
    for anim in ctx.anims:
      anim.update()
      if anim.done:
        ctx.anims.remove(anim)
      if not ctx.anims and not ctx.active:
        ctx.close()
        return

  def view(ctx):
    sprites = []
    assets = use_assets()

    sprite_hud = assets.sprites["hud" if len(ctx.store.party) == 2 else "hud_single"]
    sprite_belt = assets.sprites["belt"]
    sprite_hand = assets.sprites["hand"]
    sprite_circle = assets.sprites["circle_knight"]
    sprite_tile = assets.sprites["item_tile"]
    sprite_tileleft = assets.sprites["item_tile_left"]
    sprite_tileright = assets.sprites["item_tile_right"]
    sprite_desc = assets.sprites["item_desc"]
    font_heading = assets.ttf["english"]
    font_content = assets.ttf["normal"]
    tile_width = sprite_tile.get_width()
    tile_height = sprite_tile.get_height()

    # belt
    anim_belt = next((a for a in ctx.anims if a.target == "belt"), None)
    if anim_belt:
      if ctx.active:
        t = ease_out(anim_belt.pos)
      else:
        t = 1 - anim_belt.pos
      start_height = 0
      end_height = sprite_belt.get_height()
      belt_width = sprite_belt.get_width()
      belt_height = lerp(start_height, end_height, t)
      sprite_belt = sprite_belt.subsurface(Rect(
        (0, end_height - belt_height),
        (belt_width, belt_height)
      ))
    if anim_belt or ctx.active:
      sprites.append(Sprite(
        image=sprite_belt,
        pos=(
          Hud.MARGIN_LEFT,
          Hud.MARGIN_TOP + sprite_circle.get_height() // 2
        ),
        layer="ui"
      ))

    # "ITEM" letters
    start_x = -16
    target_x = Hud.MARGIN_LEFT
    y = Hud.MARGIN_TOP + sprite_circle.get_height() + 2
    for i, char in enumerate("item"):
      sprite_char = assets.sprites["item_" + char]
      sprite_height = sprite_char.get_height()
      anim = next((a for a in ctx.anims if a.target == char), None)
      if anim:
        if ctx.active:
          t = ease_out(anim.pos)
        else:
          t = 1 - anim.pos
        x = lerp(start_x, target_x, t)
      else:
        x = target_x
        if not ctx.active:
          sprite_char = None
      if sprite_char:
        sprites.append(Sprite(
          image=sprite_char,
          pos=(x, y),
          layer="ui"
        ))
      y += sprite_height + 2

    # grid
    cols, rows = ctx.grid_size
    cells_x = Hud.MARGIN_LEFT + sprite_belt.get_width() - 2
    cells_y = Hud.MARGIN_TOP + sprite_hud.get_height()
    for row in range(rows):
      for col in range(cols + 1):
        if col == cols and row != rows - 1:
          continue
        cell = (col, row)
        if col == 0:
          sprite = sprite_tileleft
        elif col >= cols - 1:
          sprite = sprite_tileright
        else:
          sprite = sprite_tile
        anim = next((a for a in ctx.anims if a.target == cell), None)
        if anim and type(anim) is not SelectAnim:
          if ctx.active:
            continue
          else:
            t = anim.pos
            width = lerp(tile_width, 0, t)
            height = lerp(tile_height, 0, t)
            sprite = pygame.transform.scale(sprite, (int(width), int(height)))
        elif not ctx.active:
          continue
        x = cells_x + tile_width * col + tile_width // 2 - sprite.get_width() // 2
        y = cells_y + tile_height * row + tile_height // 2 - sprite.get_height() // 2
        sprites.append(Sprite(
          image=sprite,
          pos=(x, y),
          layer="ui"
        ))

        item = None
        if ctx.selection and cell == ctx.cursor:
          item = ctx.get_item_at(ctx.selection)
        elif not ctx.selection and cell == ctx.find_extra_slot() and ctx.get_hero():
          item = ctx.get_hero().item
        elif not ctx.selection or cell != ctx.selection:
          item = ctx.get_item_at(cell)
        elif ctx.selection and cell == ctx.selection and ctx.cursor_anim.time % 2:
          item = ctx.get_item_at(ctx.cursor)

        if item and not anim:
          layer = "ui"
          if ctx.selection and cell == ctx.cursor:
            y -= 4
            layer = "hud"
          sprites.append(Sprite(
            image=item().render(),
            pos=(x, y),
            layer=layer
          ))

    # tabs
    x = cells_x + tile_width * cols
    y = cells_y
    for i, tab in enumerate(ctx.tabs):
      tab_image = assets.sprites["item_tab_h"]
      tabend_image = assets.sprites["item_tabend"]
      icon_image = assets.sprites["icon_" + tab]
      tab_anim = next((a for a in ctx.anims if a.target == tab), None)
      text_image = assets.sprites[tab] if (i == ctx.tab or type(tab_anim) is DeselectAnim or type(tab_anim) is SelectAnim) else None
      text_width = text_image.get_width() if text_image else 0
      min_width = icon_image.get_width()
      max_width = min_width + 3 + text_width
      inner_width = max_width if text_width else min_width
      true_width = inner_width + 9
      tab_width = true_width
      if tab_anim:
        t = tab_anim.pos
        if ctx.active:
          t = ease_out(t)
        else:
          t = 1 - t
        if type(tab_anim) is SelectAnim:
          tab_width = lerp(min_width, max_width, t) + 9
        elif type(tab_anim) is DeselectAnim:
          tab_width = lerp(max_width, min_width, t) + 9
        else:
          tab_width *= t
      elif not ctx.active:
        tab_width = 0
      if tab_width:
        tab_image = Surface((tab_width, 16), SRCALPHA)
        pygame.draw.rect(tab_image, BLACK, Rect((0, 0),
          (tab_width - 1, tab_image.get_height() - 3)))
        tab_image.blit(icon_image, (3, 3))
        if text_image:
          tab_image.blit(text_image, (
            3 + icon_image.get_width() + 4,
            tab_image.get_height() / 2 - text_image.get_height() / 2 - 1))
        tab_image.blit(tabend_image, (tab_width - tabend_image.get_width(), 0))
        if i != ctx.tab:
          tab_image = replace_color(tab_image, WHITE, GRAY)
        sprites.append(Sprite(
          image=tab_image,
          pos=(x, y),
          layer="ui"
        ))
      y += tab_image.get_height() - 2

    # selection
    if ctx.selection:
      cursor_image = Surface((tile_width, tile_height), SRCALPHA)
      cursor_col, cursor_row = ctx.selection
      cursor_x = cells_x + tile_width * cursor_col
      cursor_y = cells_y + tile_height * cursor_row
      cursor_color = GOLD
      if not ctx.anims and ctx.items:
        pygame.draw.rect(cursor_image, cursor_color, Rect(0, 0, tile_width, tile_height), width=1)
        sprites.append(Sprite(
          image=cursor_image,
          pos=(cursor_x, cursor_y),
          layer="ui"
        ))

    # cursor
    cursor_image = Surface((tile_width, tile_height), SRCALPHA)
    cursor_col, cursor_row = ctx.cursor
    cursor_x = cells_x + tile_width * cursor_col
    cursor_y = cells_y + tile_height * cursor_row
    cursor_color = WHITE
    if type(ctx.child) is ChoiceContext:
      cursor_color = GOLD
    elif ctx.cursor_anim.time // 2 % 2:
      cursor_color = BLUE
    if not ctx.anims and ctx.items:
      pygame.draw.rect(cursor_image, cursor_color, Rect(0, 0, tile_width, tile_height), width=1)
      sprites.append(Sprite(
        image=cursor_image,
        pos=(cursor_x, cursor_y),
        layer="ui"
      ))

    # description box
    sprite_desc = ctx.box.render()
    if sprite_desc:
      box_x = cells_x
      box_y = cells_y + tile_height * rows
      sprites.append(Sprite(
        image=sprite_desc,
        pos=(box_x, box_y),
        layer="ui"
      ))

    # choice box
    if type(ctx.child) is ChoiceContext:
      start_x = cursor_x
      target_x = cursor_x + tile_width + 4
      anim = next((a for a in ctx.child.anims if type(a) is TweenAnim), None)
      if anim:
        t = anim.pos
        if not ctx.child.exiting:
          t = ease_out(t)
        else:
          t = 1 - t
        x = lerp(start_x, target_x, t)
      else:
        x = target_x
      y = cells_y
      sprites.append(Sprite(
        image=ctx.child.render(),
        pos=(x, y),
        layer="hud"
      ))
    elif not ctx.anims and ctx.items:
      if ctx.selection:
        hand_y = cursor_y + tile_height - 3 + ctx.cursor_anim.update() * 2
        sprites.append(Sprite(
          image=rotate(sprite_hand, -90),
          pos=(cursor_x, hand_y),
          layer="hud"
        ))
      else:
        hand_x = cursor_x + tile_width - 3 + ctx.cursor_anim.update() * 2
        sprites.append(Sprite(
          image=sprite_hand,
          pos=(hand_x, cursor_y),
          layer="hud"
        ))

    # controls
    controls_anim = next((a for a in ctx.anims if a.target == "controls"), None)
    if ctx.active or controls_anim:
      controls_width = cells_x + 8
      controls_height = 21
      controls_y = WINDOW_HEIGHT - 20

      for control in ctx.controls:
        control_image = control.render()
        controls_width += control_image.get_width() + 12

      if controls_anim:
        if ctx.active:
          controls_height *= controls_anim.pos
        else:
          controls_height *= 1 - controls_anim.pos

      if not controls_anim:
        controls_x = cells_x
        for control in ctx.controls:
          control_image = control.render()
          sprites.append(Sprite(
            image=control_image,
            pos=(controls_x, controls_y),
            origin=("left", "center"),
            layer="hud",
            offset=16
          ))
          controls_x += control_image.get_width() + 12

      controls_image = Surface((controls_width, controls_height), SRCALPHA)
      pygame.draw.rect(controls_image, BLACK, Rect(0, 0, controls_image.get_width() - 1, controls_image.get_height()))
      pygame.draw.rect(controls_image, BLACK, Rect(controls_image.get_width() - 1, 1, 1, controls_image.get_height() - 2))
      sprites.insert(0, Sprite(
        image=controls_image,
        pos=(0, controls_y),
        origin=("left", "center"),
        layer="hud",
      ))

    return sprites + super().view()
