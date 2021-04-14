import random
import pygame
from pygame import Surface

from contexts import Context
from contexts.choice import ChoiceContext
from comps.bar import Bar
from assets import load as use_assets
from filters import replace_color
from keyboard import key_times
import palette

from anims.tween import TweenAnim
from easing.expo import ease_out
from lerp import lerp

SPACING = 4
MARGIN = 8
ENTER_DURATION = 8
ENTER_STAGGER = 4
EXIT_DURATION = 6
EXIT_STAGGER = 3

class InventoryContext(Context):
  def __init__(ctx, parent, inventory, on_close=None):
    super().__init__(parent)
    ctx.data = inventory
    ctx.grid_size =  (inventory.cols, inventory.rows)
    ctx.on_close = on_close
    ctx.on_animate = None
    ctx.cursor = (0, 0)
    ctx.active = True
    ctx.anims = []
    ctx.bar = Bar()
    item = ctx.get_item_at(ctx.cursor)
    ctx.select_item(item)
    ctx.enter()

  def enter(ctx, on_end=None):
    ctx.animate(active=True, on_end=on_end)
    ctx.bar.enter()

  def exit(ctx):
    ctx.animate(active=False, on_end=ctx.close)
    ctx.bar.exit()

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

    key_deltas = {
      pygame.K_LEFT: (-1, 0),
      pygame.K_RIGHT: (1, 0),
      pygame.K_UP: (0, -1),
      pygame.K_DOWN: (0, 1)
    }
    if key in key_deltas:
      delta = key_deltas[key]
      ctx.handle_move(delta)

    if key not in key_times or key_times[key] != 1:
      return False

    if key == pygame.K_RETURN:
      ctx.handle_choose()

    if key == pygame.K_BACKSPACE:
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
    menu = ctx.render_menu()
    x = MARGIN
    y = window_height - MARGIN - ctx.bar.surface.get_height() - SPACING - menu.get_height()
    surface.blit(menu, (x, y))

    if type(ctx.child) is ChoiceContext:
      menu = ctx.child.render()
      x += menu.get_width() + SPACING
      surface.blit(menu, (x, y))

  def render_menu(ctx):
    assets = use_assets()
    box = assets.sprites["box"]

    cols, rows = ctx.grid_size
    menu_width = max(0, cols * (box.get_width() + SPACING) - SPACING)
    menu_height = max(0, rows * (box.get_height() + SPACING) - SPACING)
    menu = Surface((menu_width, menu_height))
    menu.set_colorkey(0xFF00FF)
    menu.fill(0xFF00FF)

    y = 0
    for row in range(rows):
      x = 0
      for col in range(cols):
        cell = (col, row)
        sprite = box
        item = ctx.get_item_at(cell)
        new_color = None
        if item is None:
          new_color = palette.GRAY
        elif (col, row) == ctx.cursor and not ctx.anims:
          new_color = palette.YELLOW
        if new_color:
          sprite = replace_color(
            surface=sprite,
            old_color=palette.WHITE,
            new_color=new_color
          )
        t = 1 if ctx.active else 0
        box_width = box.get_width()
        box_height = box.get_height()
        box_anim = next((a for a in ctx.anims if a.target == cell), None)
        if box_anim:
          t = box_anim.update()
          if box_anim.done:
            ctx.remove_anim(box_anim)
          if ctx.active:
            t = ease_out(t)
          else:
            t = 1 - t
          box_width = round(box_width * t)
          box_height = round(box_height)
          sprite = pygame.transform.scale(sprite, (box_width, box_height))
        if t:
          menu.blit(sprite, (
            x + box.get_width() // 2 - box_width // 2,
            y + box.get_height() // 2 - box_height // 2
          ))
          if item and not ctx.anims:
            menu.blit(type(item).render(), (x + 8, y + 8))
        x += box.get_width() + SPACING
      y += box.get_height() + SPACING

    return menu
