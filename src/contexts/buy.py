from math import ceil
import pygame
from pygame import Surface, Rect, SRCALPHA
from pygame.draw import rect as draw_rect
import lib.keyboard as keyboard
import lib.gamepad as gamepad
import lib.vector as vector
from lib.sprite import Sprite, SpriteMask
from lib.filters import stroke, outline, darken_image, shadow_lite as shadow
from colors.palette import BLACK, WHITE, CYAN, CORAL, DARKCORAL
from portraits.husband import HusbandPortrait

from contexts import Context
from cores.knight import Knight
from comps.bg import Bg
from comps.box import Box
from comps.card import Card
from comps.hud import Hud
from comps.rarity import Rarity
from comps.shoptag import ShopTag
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
BOX_YMARGIN = 36
TEXTBOX_XPADDING = 12
TEXTBOX_YPADDING = 9
TEXTBOX_TITLE_MARGIN = 5
TEXTBOX_DESC_MARGIN = TEXTBOX_TITLE_MARGIN + 2
TEXTBOX_XMARGIN = 4
ENABLED_ITEM_RARITY_STARS = True

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
  shadow_color = CYAN if selected else DARKCORAL
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
  def __init__(box, width):
    box.width = width
    box.textbox = TextBox(
      font="normal",
      size=(width - TEXTBOX_XPADDING * 2, assets.ttf["normal"].height() * 2 + 4)
    )
    box.item = None

  def reload(box, item):
    box.item = item
    box.textbox.print(item.desc)
    box.cache_rarity = None

  def view(box):
    sprites = []
    item = box.item

    if "cache_bg" not in dir(box):
      box.cache_bg = Box(
        sprite_prefix="buy_textbox",
        size=(box.width, (0
          + TEXTBOX_YPADDING
          + assets.ttf["normal"].height()
          + TEXTBOX_TITLE_MARGIN
          + assets.ttf["normal"].height()
          + 4
          + assets.ttf["normal"].height()
          + TEXTBOX_DESC_MARGIN
          + assets.ttf["normal"].height()
          + TEXTBOX_YPADDING
        )),
      ).render()

    sprites.append(box_sprite := Sprite(
      image=box.cache_bg,
    ))

    sprites.append(title_sprite := Sprite(
      image=(title_image := assets.ttf["english"].render(item.name, item.color)),
      pos=(TEXTBOX_XPADDING, TEXTBOX_YPADDING),
    ))

    sprites.append(price_sprite := Sprite(
      image=(price_image := assets.ttf["english"].render(f"{item.value}G", BLACK)),
      pos=(
        box_sprite.image.get_width() - TEXTBOX_XPADDING,
        title_sprite.y
      ),
      origin=Sprite.ORIGIN_TOPRIGHT,
    ))

    sprites.append(desc_sprite := Sprite(
      image=(desc_image := box.textbox.render()),
      pos=(
        title_sprite.x,
        title_sprite.rect.bottom + TEXTBOX_TITLE_MARGIN
      ),
    ))

    sprites.append(ownedlabel_sprite := Sprite(
      image=assets.ttf["english"].render("Own", BLACK),
      pos=(
        title_sprite.x,
        desc_sprite.rect.bottom + TEXTBOX_DESC_MARGIN
      ),
    ))

    sprites.append(ownedvalue_sprite := Sprite(
      image=assets.ttf["normal"].render("0", BLACK),
      pos=(
        ownedlabel_sprite.rect.right + 4,
        ownedlabel_sprite.y
      ),
    ))

    if ENABLED_ITEM_RARITY_STARS:
      if not box.cache_rarity:
        box.cache_rarity = Rarity.render(item.rarity)
      sprites.append(rarity_sprite := Sprite(
        image=box.cache_rarity,
        pos=(
          title_sprite.rect.right + 4,
          title_sprite.y
        )
      ))

    return sprites

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
      key="grid_bg"
    )]
    if "cached_box" not in dir(ctx):
      ctx.cached_box = ctx.box.render()
      ctx.cached_box = shadow(ctx.cached_box, BLACK)
      ctx.cached_box = shadow(ctx.cached_box, BLACK)
    box_image = ctx.cached_box
    box_x = WINDOW_WIDTH - box_image.get_width() - BOX_XMARGIN
    box_y = BOX_YMARGIN
    box_view = [Sprite(image=box_image, layer="hud")]
    title_image = assets.ttf["roman_large"].render("Items")
    title_image = outline(title_image, DARKCORAL)
    title_image = shadow(title_image, BLACK)
    title_image = shadow(title_image, BLACK)
    title_view = [Sprite(
      image=title_image,
      pos=(box_x, box_y - 2),
      origin=Sprite.ORIGIN_BOTTOMLEFT,
      layer="hud",
      key="title",
    )]
    itemgrid_view = ctx.itemgrid.view()
    return backdrop_view + bg_view + Sprite.move_all(
      box_view + Sprite.move_all(
        sprites=itemgrid_view,
        offset=(ITEMGRID_XPADDING, ITEMGRID_YPADDING),
        layer="hud"
      ),
      (box_x, box_y)
    ) + title_view

class BuyContext(Context):
  def __init__(ctx, hud=None, *args, **kwargs):
    super().__init__(*args, **kwargs)
    ctx.textbox = ItemTextBox(width=128 + (28 if ENABLED_ITEM_RARITY_STARS else 0))
    ctx.gridctx = GridContext(
      items=[resolve_item(i) for i in ("Potion", "Ankh", "Elixir", "Fish", "Cheese", "Bread", "Vino", "Antidote", "MusicBox", "LovePotion", "Balloon", "Emerald", "Key")],
      height=128,
      on_change_item=ctx.textbox.reload
    )
    ctx.tag = ShopTag("general_store")
    ctx.card = Card("buy")
    ctx.hud = hud or Hud(party=[Knight()])
    ctx.portrait = HusbandPortrait()

  def enter(ctx):
    ctx.open(child=ctx.gridctx)

  def view(ctx):
    sprites = []

    grid_view = super().view()
    bg_mask = next((s for s in grid_view if s.key == "grid_bg"), None)
    if "cache_bar" not in dir(ctx):
      ctx.cache_bar = Surface((WINDOW_WIDTH - bg_mask.rect.width, 32), flags=SRCALPHA)
      ctx.cache_bar.fill(BLACK)
    sprites += grid_view

    sprites += Sprite.move_all(
      sprites=ctx.textbox.view(),
      offset=(WINDOW_WIDTH - BOX_XMARGIN - ctx.gridctx.box.width - TEXTBOX_XMARGIN, BOX_YMARGIN),
      origin=Sprite.ORIGIN_TOPRIGHT,
    )

    if "cache_tag" not in dir(ctx):
      ctx.cache_tag = ctx.tag.render()
      ctx.cache_tag = stroke(ctx.cache_tag, BLACK)
    title_sprite = next((s for s in grid_view if s.key == "title"), None)
    sprites += [tag_sprite := Sprite(
      image=ctx.cache_tag,
      pos=(BOX_XMARGIN, title_sprite.rect.top)
    )]

    card_sprite = ctx.card.render()
    card_sprite.pos = vector.add(card_sprite.pos, (
      card_sprite.rect.width / 2 + tag_sprite.rect.left,
      card_sprite.rect.height / 2 + tag_sprite.rect.bottom + 2
    ))
    sprites.append(card_sprite)

    sprites += [Sprite(
      image=ctx.cache_bar,
      pos=(0, WINDOW_HEIGHT),
      origin=Sprite.ORIGIN_BOTTOMLEFT
    )]

    sprites += [Sprite(
      image=ctx.portrait.render(),
      pos=vector.add(bg_mask.rect.bottomleft, (64, 0)),
      origin=Sprite.ORIGIN_BOTTOMRIGHT,
      layer="ui"
    )]

    sprites += [Sprite(
      image=ctx.hud.render(),
      pos=(BOX_XMARGIN, WINDOW_HEIGHT - 8),
      origin=Sprite.ORIGIN_BOTTOMLEFT,
    )]

    return sprites
