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
from comps.bg import Bg
from comps.box import Box
from comps.textbox import TextBox
from anims.sine import SineAnim
from savedata.resolve import resolve_item
import assets
from config import WINDOW_SIZE, WINDOW_WIDTH, WINDOW_HEIGHT

GRID_COLS = 3
ITEM_WIDTH = 32
ITEM_HEIGHT = 32
ITEMGRID_XPADDING = 12
ITEMGRID_YPADDING = 12
PRICETAG_XPADDING = 3
PRICETAG_YPADDING = 2
BOX_XMARGIN = 24
BOX_YMARGIN = 24
TEXTBOX_XPADDING = 12
TEXTBOX_YPADDING = 12
TEXTBOX_TITLE_MARGIN = 5
TEXTBOX_XMARGIN = 4

class CursorAnim(SineAnim): pass

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
    grid.cursor_drawn = grid.project_index(0)
    grid.cursor_anim = CursorAnim(period=30)
    grid.scroll = 0
    grid.scroll_drawn = 0

  @property
  def width(grid):
    return grid.cols * ITEM_WIDTH

  @property
  def rows(grid):
    return ceil(len(grid.items) / grid.cols)

  @property
  def visible_rows(grid):
    return ceil(grid.height / ITEM_HEIGHT)

  @property
  def item(grid):
    return grid.items[grid.selection]

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
    if row < grid.scroll + 1:
      grid.scroll = max(0, row - 1)
    elif row > grid.scroll + (grid.visible_rows - 2):
      grid.scroll = row - grid.visible_rows // 2
    return True

  def view(grid):
    items_view = grid.view_items()
    grid.scroll_drawn += (grid.scroll - grid.scroll_drawn) / 8
    scroll_offset = (0, grid.scroll_drawn * -ITEM_HEIGHT)
    return [SpriteMask(
      size=(grid.width, grid.height),
      children=Sprite.move_all(
        [s for s in items_view if s.key != "pricetag"],
        scroll_offset
      )
    )] + Sprite.move_all(
      [s for s in items_view if s.key == "pricetag" if s.rect.bottom + scroll_offset[1] >= 0 and s.rect.top + scroll_offset[1] < grid.height]
        + grid.view_cursor(),
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
    selection_col, selection_row = grid.project_index(grid.selection)
    drawn_col, drawn_row = grid.cursor_drawn
    drawn_col += (selection_col - drawn_col) / 4
    drawn_row += (selection_row - drawn_row) / 4
    grid.cursor_drawn = (drawn_col, drawn_row)
    grid.cursor_anim.update()
    cursor_image = assets.sprites["hand"]
    return [Sprite(
      image=cursor_image,
      pos=(
        drawn_col * ITEM_WIDTH + 8 + grid.cursor_anim.pos * 2,
        (drawn_row + 0.5) * ITEM_HEIGHT
      ),
      origin=Sprite.ORIGIN_RIGHT,
      flip=(True, False),
      layer="hud"
    )]

class ItemTextBox:
  def __init__(box, size):
    box.bg = Box(
      sprite_prefix="buy_textbox",
      size=size,
    )
    box.textbox = TextBox(
      font="normal",
      size=vector.subtract(size, (TEXTBOX_XPADDING * 2, TEXTBOX_YPADDING * 2))
    )
    box.item = None

  def reload(box, item):
    box.item = item
    box.textbox.print(item.desc)

  def view(box):
    item = box.item
    title_image = assets.ttf["english"].render(item.name, item.color)
    return [
      Sprite(image=box.bg.render()),
      Sprite(
        image=title_image,
        pos=(TEXTBOX_XPADDING, TEXTBOX_YPADDING),
      ),
      Sprite(
        image=box.textbox.render(),
        pos=(TEXTBOX_XPADDING, TEXTBOX_YPADDING + title_image.get_height() + TEXTBOX_TITLE_MARGIN),
      ),
    ]

class GridContext(Context):
  def __init__(ctx, items, height=0, on_change_item=None, *args, **kwargs):
    super().__init__(*args, **kwargs)
    ctx.height = height
    ctx.itemgrid = ItemStickyGrid(
      cols=GRID_COLS,
      items=items,
      height=height and (height - ITEMGRID_YPADDING * 2) or 0
    )
    ctx.box = Box(
      sprite_prefix="buy_box",
      size=(
        ctx.itemgrid.width + ITEMGRID_XPADDING * 2,
        ctx.itemgrid.height + ITEMGRID_YPADDING * 2
      )
    )
    ctx.bg = Bg((ctx.box.width + BOX_XMARGIN * 2, WINDOW_HEIGHT))
    ctx.cursor = (0, 0)
    ctx.on_change_item = on_change_item
    on_change_item and on_change_item(ctx.item)

  @property
  def item(ctx):
    return ctx.itemgrid.item

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
      ctx.on_change_item and ctx.on_change_item(ctx.item)
    return selected

  def view(ctx):
    backdrop_image = Surface(WINDOW_SIZE, flags=SRCALPHA)
    backdrop_image.fill(WHITE)
    backdrop_view = [Sprite(image=backdrop_image)]
    bg_view = [SpriteMask(
      pos=(WINDOW_WIDTH - ctx.bg.width, 0),
      size=ctx.bg.size,
      children=ctx.bg.view(),
    )]
    box_image = ctx.box.render()
    box_view = [Sprite(image=box_image)]
    itemgrid_view = ctx.itemgrid.view()
    return backdrop_view + bg_view + Sprite.move_all(
      box_view + Sprite.move_all(
        itemgrid_view,
        (ITEMGRID_XPADDING, ITEMGRID_YPADDING)
      ),
      (WINDOW_WIDTH - box_image.get_width() - 24, 24)
    )

class BuyContext(Context):
  def __init__(ctx, *args, **kwargs):
    super().__init__(*args, **kwargs)
    ctx.textbox = ItemTextBox(size=(128, 58))
    ctx.gridctx = GridContext(
      items=[resolve_item(i) for i in ("Potion", "Ankh", "Elixir", "Fish", "Cheese", "Bread", "Vino", "Antidote", "MusicBox", "LovePotion", "Balloon", "Emerald", "Key")],
      height=128,
      on_change_item=ctx.textbox.reload
    )

  def enter(ctx):
    ctx.open(child=ctx.gridctx)

  def view(ctx):
    return super().view() + Sprite.move_all(
      sprites=ctx.textbox.view(),
      offset=(WINDOW_WIDTH - BOX_XMARGIN - ctx.gridctx.box.width - TEXTBOX_XMARGIN, BOX_YMARGIN),
      origin=Sprite.ORIGIN_TOPRIGHT,
    )
