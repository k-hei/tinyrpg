import random
import pygame
from pygame import Surface, Rect

from contexts import Context
from contexts.choice import ChoiceContext
from comps.hud import Hud
from comps.bar import Bar
from assets import load as use_assets
from filters import replace_color
from keyboard import key_times, ARROW_DELTAS
import palette

from anims.tween import TweenAnim
from anims.sine import SineAnim
from easing.expo import ease_out
from lerp import lerp

SPACING = 4
MARGIN = 8
ENTER_DURATION = 8
ENTER_STAGGER = 3
EXIT_DURATION = 6
EXIT_STAGGER = 3
DURATION_BELTENTER = 15

class InventoryContext(Context):
  def __init__(ctx, parent, inventory, on_close=None):
    super().__init__(parent)
    ctx.data = inventory
    ctx.grid_size =  (inventory.cols, inventory.rows)
    ctx.on_close = on_close
    ctx.on_animate = None
    ctx.cursor = (0, 0)
    ctx.cursor_anim = SineAnim(period=30)
    ctx.active = True
    ctx.anims = []
    ctx.bar = Bar()
    item = ctx.get_item_at(ctx.cursor)
    ctx.select_item(item)
    ctx.enter()

  def enter(ctx, on_end=None):
    ctx.bar.enter()
    ctx.anims.append(TweenAnim(duration=DURATION_BELTENTER, target="belt"))

    for i, char in enumerate("item"):
      ctx.anims.append(TweenAnim(
        duration=9,
        delay=4 * (i + 1),
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
    # ctx.animate(active=False, on_end=ctx.close)
    ctx.bar.exit()
    ctx.close()

  def animate(ctx, active, on_end=None):
    DURATION = ENTER_DURATION if active else EXIT_DURATION
    STAGGER = ENTER_STAGGER if active else EXIT_STAGGER
    cols, rows = ctx.grid_size
    ctx.active = active
    cells = []
    for row in range(rows):
      for col in range(cols):
        cells.append((col, row))
    random.shuffle(cells)
    index = 0
    for col, row in cells:
      ctx.anims.append(TweenAnim(
        duration=DURATION,
        delay=STAGGER * index,
        target=(col, row)
      ))
      index += 1
    ctx.on_animate = on_end

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

  def select_item(ctx, item=None):
    if item is None:
      item = ctx.get_item_at(ctx.cursor)

    if item is None:
      ctx.bar.print("Your pack is currently empty.")
    else:
      ctx.bar.print(item.name + ": " + item.desc)

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
      ctx.select_item(target_item)

  def handle_choose(ctx):
    item = ctx.get_item_at(ctx.cursor)
    if item:
      def use_item():
        success, message = ctx.parent.use_item(item)
        if not success:
          ctx.bar.print(message)
          return False
        else:
          ctx.exit()
          return True

      def discard_item():
        ctx.data.items.remove(item)
        ctx.select_item()
        return True

      ctx.child = ChoiceContext(
        parent=ctx,
        choices=("Use", "Discard"),
        on_choose=lambda choice: (
          choice == "Use" and use_item() or
          choice == "Discard" and discard_item()
        )
      )

  def draw(ctx, surface):
    assets = use_assets()
    window_width = surface.get_width()
    window_height = surface.get_height()

    ctx.bar.draw(surface)

    sprite_hud = assets.sprites["hud"]
    sprite_belt = assets.sprites["belt"]
    sprite_hand = assets.sprites["hand"]
    sprite_circle = assets.sprites["circle_knight"]
    sprite_tile = assets.sprites["item_tile"]
    sprite_tileleft = assets.sprites["item_tile_left"]
    sprite_tileright = assets.sprites["item_tile_right"]
    tile_width = sprite_tile.get_width()
    tile_height = sprite_tile.get_height()

    for anim in ctx.anims:
      anim.update()
      if anim.done:
        ctx.anims.remove(anim)

    anim_belt = next((a for a in ctx.anims if a.target == "belt"), None)
    if anim_belt:
      t = ease_out(anim_belt.pos)
      start_height = 0
      end_height = sprite_belt.get_height()
      belt_width = sprite_belt.get_width()
      belt_height = lerp(start_height, end_height, t)
      sprite_belt = sprite_belt.subsurface(Rect(
        (0, end_height - belt_height),
        (belt_width, belt_height)
      ))

    surface.blit(sprite_belt, (
      Hud.MARGIN_LEFT,
      Hud.MARGIN_TOP + sprite_circle.get_height() // 2
    ))

    start_x = -16
    target_x = Hud.MARGIN_LEFT
    y = Hud.MARGIN_TOP + sprite_circle.get_height() + 2
    for i, char in enumerate("item"):
      sprite_char = assets.sprites["item_" + char]
      anim = next((a for a in ctx.anims if a.target == char), None)
      if anim:
        t = ease_out(anim.pos)
        x = lerp(start_x, target_x, t)
      else:
        x = target_x
      surface.blit(sprite_char, (x, y))
      y += sprite_char.get_height() + 2

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
          continue
        x = cells_x + tile_width * col + tile_width // 2 - sprite.get_width() // 2
        y = cells_y + tile_height * row + tile_height // 2 - sprite.get_height() // 2
        surface.blit(sprite, (x, y))
        item = ctx.get_item_at(cell)
        if item and not anim:
          surface.blit(item.render(), (x, y))

    if not ctx.anims:
      cursor_col, cursor_row = ctx.cursor
      cursor_color = palette.BLUE if ctx.cursor_anim.time % 2 or type(ctx.child) is ChoiceContext else palette.WHITE
      cursor_x = cells_x + tile_width * cursor_col
      cursor_y = cells_y + tile_height * cursor_row
      pygame.draw.rect(surface, cursor_color, Rect(cursor_x, cursor_y, tile_width, tile_height), width=1)

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
