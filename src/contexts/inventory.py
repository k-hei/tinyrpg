import random
import pygame
from pygame import Surface, Rect, SRCALPHA

from contexts import Context
from contexts.choice import ChoiceContext, Choice
from comps.hud import Hud
from comps.invdesc import InventoryDescription
from assets import load as use_assets
from filters import replace_color
import lib.gamepad as gamepad
import keyboard
from keyboard import key_times, ARROW_DELTAS
from colors.palette import BLACK, WHITE, GRAY, BLUE
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
    ctx.active = True
    ctx.anims = []
    ctx.box = InventoryDescription()
    ctx.grid_size = (INVENTORY_COLS, INVENTORY_ROWS)
    ctx.items = []
    ctx.update_items()

  def enter(ctx, on_end=None):
    ctx.select()
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

  def remove_anim(ctx, anim):
    if anim in ctx.anims:
      ctx.anims.remove(anim)
    if not ctx.anims and ctx.on_animate:
      ctx.on_animate()

  def get_item_at(ctx, cell):
    cols, rows = ctx.grid_size
    col, row = cell
    index = row * cols + col
    if index >= len(ctx.items) or not ctx.contains(cell):
      return None
    return ctx.items[index]

  def get_selected_item(ctx):
    return ctx.get_item_at(ctx.cursor)

  def select(ctx, item=None):
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

    if keyboard.get_pressed(button) > 1:
      return False

    if button in ARROW_DELTAS:
      delta = ARROW_DELTAS[button]
      ctx.handle_move(delta)

    if gamepad.get_state(gamepad.L):
      ctx.handle_tab(delta=-1)

    if gamepad.get_state(gamepad.R):
      ctx.handle_tab(delta=1)

    if button == pygame.K_TAB:
      if (keyboard.get_pressed(pygame.K_LSHIFT)
      or keyboard.get_pressed(pygame.K_RSHIFT)
      ):
        ctx.handle_tab(delta=-1)
      else:
        ctx.handle_tab(delta=1)

    if button in (pygame.K_RETURN, pygame.K_SPACE, gamepad.controls.confirm):
      ctx.handle_choose()

    if button in (pygame.K_BACKSPACE, pygame.K_ESCAPE, gamepad.controls.cancel, gamepad.controls.item):
      ctx.exit()

  def handle_move(ctx, delta):
    delta_x, delta_y = delta
    cursor_x, cursor_y = ctx.cursor
    target_cell = (cursor_x + delta_x, cursor_y + delta_y)
    target_item = ctx.get_item_at(target_cell)
    if target_item:
      ctx.cursor = target_cell
      ctx.select(target_item)

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
    ctx.select()

  def handle_choose(ctx):
    if ctx.get_item_at(ctx.cursor) is None:
      return False
    ctx.open(ChoiceContext(choices=[
      Choice(text="Use"),
      Choice(text="Carry"),
      Choice(text="Drop", closing=True)
    ], on_choose=lambda choice: (
      choice.text == "Use" and ctx.use_item()
      or choice.text == "Carry" and ctx.carry_item()
      or choice.text == "Drop" and ctx.drop_item()
    )))
    return True

  def use_item(ctx, item=None):
    item = item or ctx.get_selected_item()
    if "use_item" in dir(ctx.parent):
      success, message = ctx.parent.use_item(item)
    else:
      success, message = ctx.parent.store.use_item(item)
    if success:
      ctx.exit()
      return True
    else:
      ctx.box.print(message)
      return False

  def carry_item(ctx, item=None):
    item = item or ctx.get_selected_item()
    if "carry_item" in dir(ctx.parent):
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
      for col in range(cols):
        cell = (col, row)
        if col == 0:
          sprite = sprite_tileleft
        elif col == cols - 1:
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
        item = ctx.get_item_at(cell)
        if item and not anim:
          sprites.append(Sprite(
            image=item().render(),
            pos=(x, y),
            layer="ui"
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
          (tab_width - 1, tab_image.get_height() - 1)))
        tab_image.blit(icon_image, (3, 3))
        if text_image:
          tab_image.blit(text_image, (
            3 + icon_image.get_width() + 3,
            tab_image.get_height() / 2 - text_image.get_height() / 2 - 1))
        tab_image.blit(tabend_image, (tab_width - tabend_image.get_width(), 0))
        if i != ctx.tab:
          tab_image = replace_color(tab_image, WHITE, GRAY)
        sprites.append(Sprite(
          image=tab_image,
          pos=(x, y),
          layer="ui"
        ))
      y += tab_image.get_height() + 1

    # cursor
    cursor_image = Surface((tile_width, tile_height), SRCALPHA)
    cursor_col, cursor_row = ctx.cursor
    cursor_x = cells_x + tile_width * cursor_col
    cursor_y = cells_y + tile_height * cursor_row
    cursor_color = BLUE if ctx.cursor_anim.time % 2 or type(ctx.child) is ChoiceContext else WHITE
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
      hand_x = cursor_x + tile_width - 3 + ctx.cursor_anim.update() * 2
      sprites.append(Sprite(
        image=sprite_hand,
        pos=(hand_x, cursor_y),
        layer="hud"
      ))

    return sprites + super().view()
