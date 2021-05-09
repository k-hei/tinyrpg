import random
import pygame
from pygame import Surface, Rect

from contexts import Context
from contexts.choice import ChoiceContext
from comps.hud import Hud
from comps.invdesc import InventoryDescription
from assets import load as use_assets
from filters import replace_color
from keyboard import key_times, ARROW_DELTAS
import palette

from anims.tween import TweenAnim
from anims.sine import SineAnim
from easing.expo import ease_out
from lib.lerp import lerp

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

class InventoryContext(Context):
  def __init__(ctx, inventory, on_close=None):
    super().__init__()
    ctx.data = inventory
    ctx.grid_size =  (inventory.cols, inventory.rows)
    ctx.on_close = on_close
    ctx.on_animate = None
    ctx.cursor = (0, 0)
    ctx.cursor_anim = SineAnim(period=30)
    ctx.active = True
    ctx.anims = []
    ctx.box = InventoryDescription()

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

  def exit(ctx):
    ctx.active = False
    ctx.box.exit()
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

  def remove_anim(ctx, anim):
    if anim in ctx.anims:
      ctx.anims.remove(anim)
    if not ctx.anims and ctx.on_animate:
      ctx.on_animate()

  def get_item_at(ctx, cell):
    inventory = ctx.data
    cols, rows = ctx.grid_size
    col, row = cell
    index = row * cols + col
    if index >= len(inventory.items) or not ctx.contains(cell):
      return None
    return inventory.items[index]

  def get_selected_item(ctx):
    return ctx.get_item_at(ctx.cursor)

  def select(ctx, item=None):
    if item is None:
      item = ctx.get_item_at(ctx.cursor)
    if item:
      ctx.box.print(item)
    else:
      ctx.box.print("Your pack is empty.")

  def use(ctx):
    item = ctx.get_selected_item()
    success, message = ctx.parent.use_item(item)
    if not success:
      ctx.box.print(message)
      return False
    else:
      ctx.exit()
      return True

  def discard(ctx):
    item = ctx.get_selected_item()
    ctx.data.items.remove(item)
    ctx.select()
    return True

  def contains(ctx, cell):
    cols, rows = ctx.grid_size
    col, row = cell
    return col >= 0 and col < cols and row >= 0 and row < rows

  def handle_keydown(ctx, key):
    if ctx.anims:
      return False

    if ctx.child:
      return ctx.child.handle_keydown(key)

    if key not in key_times or key_times[key] != 1:
      return False

    if key in ARROW_DELTAS:
      delta = ARROW_DELTAS[key]
      ctx.handle_move(delta)

    if key == pygame.K_RETURN or key == pygame.K_SPACE:
      ctx.handle_choose()

    if key == pygame.K_BACKSPACE or key == pygame.K_ESCAPE:
      ctx.exit()

  def handle_move(ctx, delta):
    delta_x, delta_y = delta
    cursor_x, cursor_y = ctx.cursor
    target_cell = (cursor_x + delta_x, cursor_y + delta_y)
    target_item = ctx.get_item_at(target_cell)
    if target_item:
      ctx.cursor = target_cell
      ctx.select(target_item)

  def handle_choose(ctx):
    ctx.child = ChoiceContext(
      parent=ctx,
      choices=("Use", "Discard"),
      on_choose=lambda choice: (
        choice == "Use" and ctx.use() or
        choice == "Discard" and ctx.discard()
      )
    )

  def draw(ctx, surface):
    assets = use_assets()
    window_width = surface.get_width()
    window_height = surface.get_height()

    sprite_hud = assets.sprites["hud"]
    sprite_belt = assets.sprites["belt"]
    sprite_hand = assets.sprites["hand"]
    sprite_circle = assets.sprites["circle_knight"]
    sprite_tile = assets.sprites["item_tile"]
    sprite_tileleft = assets.sprites["item_tile_left"]
    sprite_tileright = assets.sprites["item_tile_right"]
    sprite_desc = assets.sprites["item_desc"]
    font_heading = assets.ttf["english"]
    font_content = assets.ttf["roman"]
    tile_width = sprite_tile.get_width()
    tile_height = sprite_tile.get_height()

    # update anims
    for anim in ctx.anims:
      anim.update()
      if anim.done:
        ctx.anims.remove(anim)
      if not ctx.anims and not ctx.active:
        return ctx.close()

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
      surface.blit(sprite_belt, (
        Hud.MARGIN_LEFT,
        Hud.MARGIN_TOP + sprite_circle.get_height() // 2
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
        surface.blit(sprite_char, (x, y))
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
        if anim:
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
        surface.blit(sprite, (x, y))
        item = ctx.get_item_at(cell)
        if item and not anim:
          surface.blit(item.render(), (x, y))

    # cursor
    cursor_col, cursor_row = ctx.cursor
    cursor_color = palette.BLUE if ctx.cursor_anim.time % 2 or type(ctx.child) is ChoiceContext else palette.WHITE
    cursor_x = cells_x + tile_width * cursor_col
    cursor_y = cells_y + tile_height * cursor_row
    if not ctx.anims:
      pygame.draw.rect(surface, cursor_color, Rect(cursor_x, cursor_y, tile_width, tile_height), width=1)

    # description box
    sprite_desc = ctx.box.render()
    if sprite_desc:
      box_x = cells_x
      box_y = cells_y + tile_height * rows
      surface.blit(sprite_desc, (box_x, box_y))

    # choice box
    if type(ctx.child) is ChoiceContext:
      start_x = cursor_x
      target_x = cursor_x + tile_width + 4
      if ctx.child.anims:
        t = ctx.child.anims[0].pos
        if not ctx.child.exiting:
          t = ease_out(t)
        else:
          t = 1 - t
        x = lerp(start_x, target_x, t)
      else:
        x = target_x
      y = cells_y
      surface.blit(ctx.child.render(), (x, y))
    elif not ctx.anims:
      hand_x = cursor_x + tile_width - 3 + ctx.cursor_anim.update() * 2
      surface.blit(sprite_hand, (hand_x, cursor_y))
