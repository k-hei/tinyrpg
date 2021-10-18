from math import ceil
import pygame
from pygame import Surface, Rect, SRCALPHA
from pygame.draw import rect as draw_rect
import lib.keyboard as keyboard
import lib.gamepad as gamepad
import lib.vector as vector
from lib.sprite import Sprite, SpriteMask
from lib.filters import stroke, darken_image, shadow_lite as shadow
from colors.palette import BLACK, WHITE, CYAN, CORAL

from contexts import Context
from comps.box import Box
from savedata.resolve import resolve_item
import assets
from config import WINDOW_SIZE

GRID_COLS = 3
ITEM_WIDTH = 32
ITEM_HEIGHT = 32
ITEMGRID_XPADDING = 12
ITEMGRID_YPADDING = 12
PRICETAG_XPADDING = 3
PRICETAG_YPADDING = 2

def view_item_sticky(item, selected=False):
  sticky_image = assets.sprites["buy_sticky"]
  item_image = item().render()
  price_image = assets.ttf["english"].render(str(item.value))
  pricetag_image = Surface((
    price_image.get_width() + PRICETAG_XPADDING * 2,
    price_image.get_height() + PRICETAG_YPADDING * 2
  ), flags=SRCALPHA)
  pricetag_color = CYAN if selected else BLACK
  shadow_color = CYAN if selected else CORAL
  draw_rect(pricetag_image, pricetag_color, Rect(
    (2, 0),
    (pricetag_image.get_width() - 4, pricetag_image.get_height())
  ))
  draw_rect(pricetag_image, pricetag_color, Rect(
    (1, 1),
    (pricetag_image.get_width() - 2, pricetag_image.get_height() - 2)
  ))
  draw_rect(pricetag_image, pricetag_color, Rect(
    (0, 2),
    (pricetag_image.get_width(), pricetag_image.get_height() - 4)
  ))
  pricetag_image.blit(price_image, (PRICETAG_XPADDING, PRICETAG_YPADDING))
  pricetag_image = stroke(pricetag_image, WHITE)
  return [
    Sprite(image=shadow(sticky_image, shadow_color, i=2)),
    Sprite(
      image=item_image,
      pos=(sticky_image.get_width() / 2, sticky_image.get_height() / 2 + 1),
      origin=Sprite.ORIGIN_CENTER,
    ),
    Sprite(
      image=pricetag_image,
      pos=(sticky_image.get_width() / 2 + 1, 3),
      origin=Sprite.ORIGIN_LEFT,
      layer="hud",
      key="pricetag"
    )
  ]

class ItemStickyGrid:
  def __init__(grid, items, cols, height=0):
    grid.items = items
    grid.cols = cols
    grid.height = height or (ceil(len(grid.items) / grid.cols) // 1 * ITEM_HEIGHT)
    grid.selection = 0
    grid.scroll = 0
    grid.scroll_drawn = 0

  @property
  def width(grid):
    return grid.cols * ITEM_WIDTH

  def flatten_cell(grid, cell):
    col, row = cell
    index = row * grid.cols + col
    if (index < 0 or index >= len(grid.items)
    or col < 0 or col >= grid.cols):
      return -1
    return index

  def project_index(grid, index):
    if index < 0 or index >= len(grid.items):
      return None
    col = index % grid.cols
    row = index // grid.cols
    if col < 0 or col >= grid.cols:
      return -1
    return (col, row)

  def select(grid, cell):
    col, row = cell
    index = grid.flatten_cell(cell)
    if index == -1:
      return False
    grid.selection = index
    grid.scroll = row
    return True

  def view(grid):
    items_view = grid.view_items()
    grid.scroll_drawn += (grid.scroll - grid.scroll_drawn) / 8
    scroll_offset = (0, grid.scroll_drawn * -ITEM_HEIGHT)
    return [SpriteMask(
      size=(grid.width + ITEMGRID_XPADDING * 2, grid.height),
      children=Sprite.move_all(
        [s for s in items_view if s.key != "pricetag"],
        scroll_offset
      )
    )] + Sprite.move_all(
      [s for s in (
        [s for s in items_view if s.key == "pricetag"]
        + grid.view_cursor()
      ) if s.pos[1] + scroll_offset[1] >= 0 and s.pos[1] + scroll_offset[1] < grid.height],
      scroll_offset
    )

  def view_items(grid):
    sprites = []
    item_x = 0
    item_y = 0
    for i, item in enumerate(grid.items):
      item_view = view_item_sticky(item, selected=(i == grid.selection))
      Sprite.move_all(item_view, (item_x, item_y))
      sprites += item_view
      item_x += ITEM_WIDTH
      if item_x >= ITEM_WIDTH * GRID_COLS:
        item_x = 0
        item_y += ITEM_HEIGHT
    return sprites

  def view_cursor(grid):
    cursor_col, cursor_row = grid.project_index(grid.selection)
    cursor_image = assets.sprites["hand"]
    return [Sprite(
      image=cursor_image,
      pos=(
        cursor_col * ITEM_WIDTH + 8,
        (cursor_row + 0.5) * ITEM_HEIGHT
      ),
      origin=Sprite.ORIGIN_RIGHT,
      flip=(True, False)
    )]

class GridContext(Context):
  def __init__(ctx, items, height=0, *args, **kwargs):
    super().__init__(*args, **kwargs)
    ctx.height = height
    ctx.itemgrid = ItemStickyGrid(
      cols=GRID_COLS,
      items=items,
      height=height and (height - ITEMGRID_YPADDING * 2) or 0
    )
    ctx.box = Box(
      sprite_prefix="buy_box",
      tile_size=16,
      size=(
        ctx.itemgrid.width + ITEMGRID_XPADDING * 2,
        ctx.itemgrid.height + ITEMGRID_YPADDING * 2
      )
    )
    ctx.cursor = (0, 0)

  def handle_press(ctx, button):
    if keyboard.get_state(button) + gamepad.get_state(button) > 1:
      return

    if button in keyboard.ARROW_DELTAS:
      delta = keyboard.ARROW_DELTAS[button]
      return ctx.handle_move(delta)

  def handle_move(ctx, delta):
    target_cell = vector.add(ctx.cursor, delta)
    selected = ctx.itemgrid.select(cell=target_cell)
    if selected:
      ctx.cursor = target_cell
    return selected

  def view(ctx):
    bg_image = Surface(WINDOW_SIZE, flags=SRCALPHA)
    bg_image.fill(WHITE)
    bg_view = [Sprite(image=bg_image)]
    box_view = [Sprite(image=ctx.box.render())]
    itemgrid_view = ctx.itemgrid.view()
    return bg_view + Sprite.move_all(
      box_view + Sprite.move_all(
        itemgrid_view,
        (ITEMGRID_XPADDING, ITEMGRID_YPADDING)
      ),
      (24, 24)
    )

class BuyContext(Context):
  def enter(ctx):
    ctx.open(child=GridContext(
      items=[resolve_item(i) for i in ("Potion", "Ankh", "Elixir", "Fish", "Cheese", "Bread", "Vino", "Antidote", "MusicBox", "LovePotion", "Balloon", "Emerald", "Key")],
      height=112
    ))
