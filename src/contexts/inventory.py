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

from items import get_color

from anims.tween import TweenAnim
from anims.sine import SineAnim
from easing.expo import ease_out
from lerp import lerp

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
  def __init__(ctx, parent, inventory, on_close=None):
    super().__init__(parent)
    ctx.data = inventory
    ctx.grid_size =  (inventory.cols, inventory.rows)
    ctx.on_close = on_close
    ctx.on_animate = None
    ctx.cursor = (0, 0)
    ctx.cursor_anim = SineAnim(period=30)
    ctx.desc_x = 0
    ctx.desc_y = 0
    ctx.desc_index = 0
    ctx.desc_surface = None
    ctx.active = True
    ctx.anims = []
    ctx.bar = Bar()
    item = ctx.get_item_at(ctx.cursor)
    ctx.select_item(item)
    ctx.enter()

  def enter(ctx, on_end=None):
    ctx.bar.enter()
    ctx.anims.append(TweenAnim(duration=DURATION_BELTENTER, target="belt"))
    ctx.anims.append(TweenAnim(duration=DURATION_DESCENTER, target="desc"))
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
    ctx.bar.exit()
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

  def select_item(ctx, item=None):
    if item is None:
      item = ctx.get_item_at(ctx.cursor)

    if item is None:
      ctx.bar.print("Your pack is currently empty.")
    else:
      ctx.desc_x = 0
      ctx.desc_y = 0
      ctx.desc_index = 0
      ctx.desc_surface = None

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
    anim_desc = next((a for a in ctx.anims if a.target == "desc"), None)
    if anim_desc:
      t = anim_desc.pos
      if ctx.active:
        t = ease_out(t)
      else:
        t = 1 - t
      start_height = 0
      end_height = sprite_desc.get_height()
      sprite_height = lerp(start_height, end_height, t)
      sprite_desc = sprite_desc.subsurface(Rect(
        (0, 0),
        (sprite_desc.get_width(), sprite_height)
      ))

    if anim_desc or ctx.active:
      box_x = cells_x
      box_y = cells_y + tile_height * rows
      surface.blit(sprite_desc, (box_x, box_y))

    if not anim_desc and ctx.active:
      item = ctx.get_item_at(ctx.cursor)
      item_name = font_heading.render(item.name, get_color(item))
      surface.blit(item_name, (box_x + DESC_PADDING_X, box_y + DESC_PADDING_Y))

      if ctx.desc_surface is None:
        ctx.desc_surface = Surface((
          sprite_desc.get_width() - DESC_PADDING_X * 2,
          sprite_desc.get_height() - DESC_PADDING_Y * 2 - DESC_TITLE_SPACING - item_name.get_height()
        )).convert_alpha()
      if ctx.desc_index < len(item.desc):
        if ctx.desc_index == 0 or item.desc[ctx.desc_index] == " ":
          next_space = item.desc.find(" ", ctx.desc_index + 1)
          if next_space == -1:
            word = item.desc[ctx.desc_index+1:]
          else:
            word = item.desc[ctx.desc_index+1:next_space]
          word_width, word_height = font_content.size(word)
          if ctx.desc_x + word_width > ctx.desc_surface.get_width():
            ctx.desc_x = 0
            ctx.desc_y += word_height + DESC_LINE_SPACING
            ctx.desc_index += 1
        char = item.desc[ctx.desc_index]
        text = font_content.render(char, 0x000000)
        ctx.desc_surface.blit(text, (ctx.desc_x, ctx.desc_y))
        ctx.desc_x += text.get_width()
        ctx.desc_index += 1

      desc_x = box_x + DESC_PADDING_X
      desc_y = box_y + DESC_PADDING_Y + DESC_TITLE_SPACING + item_name.get_height()
      surface.blit(ctx.desc_surface, (desc_x, desc_y))

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

    # bar (obsolete)
    # ctx.bar.draw(surface)
