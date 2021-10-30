from math import ceil
import pygame
from pygame import Surface, Rect, SRCALPHA
from pygame.draw import rect as draw_rect
import lib.keyboard as keyboard
import lib.gamepad as gamepad
import lib.vector as vector
from lib.sprite import Sprite, SpriteMask
from lib.filters import stroke, outline, replace_color, darken_image, shadow_lite as shadow
from colors.palette import BLACK, WHITE, YELLOW, GOLD, CYAN, CORAL, BROWN, DARKBROWN
from portraits.husband import HusbandPortrait

from contexts import Context
from cores.knight import Knight
from comps.bg import Bg
from comps.box import Box
from comps.card import Card
from comps.goldbubble import GoldBubble
from comps.hud import Hud
from comps.rarity import Rarity
from comps.shoptag import ShopTag
from comps.textbox import TextBox
from comps.textbubble import TextBubble
from anims.sine import SineAnim
from savedata.resolve import resolve_item
import assets
from config import WINDOW_SIZE, WINDOW_WIDTH, WINDOW_HEIGHT

GRID_COLS = 3
ITEM_WIDTH = 40
ITEM_HEIGHT = 32
ITEMGRID_XPADDING = 0
ITEMGRID_YPADDING = 0
PRICETAG_XPADDING = 3
PRICETAG_YPADDING = 2
BOX_XMARGIN = 24
BOX_YMARGIN = 36
BG_Y = 32
BG_HEIGHT = 112
TEXTBOX_LPADDING = 8
TEXTBOX_RPADDING = 2
TEXTBOX_YPADDING = 6
TEXTBOX_ICON_MARGIN = 4
TEXTBOX_TITLE_MARGIN = 4
TEXTBOX_DESC_MARGIN = 3
TEXTBOX_XMARGIN = 4
ENABLED_ITEM_RARITY_STARS = False
ITEMS = (
  "Potion",
  "Ankh",
  "Elixir",
  "Fish",
  "Cheese",
  "Bread",
  "Vino",
  "Berry",
  "Antidote",
  "MusicBox",
  "LovePotion",
  "Balloon",
  "Emerald",
  "Key",
)

class CursorAnim(SineAnim): pass

def view_itemcell(item, selected=True, cache={}):
  sprites = []

  sheet_image = assets.sprites["buy_itemsheet"]
  if not selected:
    if "sheet" not in cache:
      cache["sheet"] = darken_image(sheet_image)
    sheet_image = cache["sheet"]
  sprites += [sheet_sprite := Sprite(image=sheet_image)]

  item_image = item().render()
  item_image = stroke(item_image, WHITE)
  if not selected:
    if item not in cache:
      cache[item] = darken_image(item_image)
    item_image = cache[item]
  sprites += [item_sprite := Sprite(
    image=item_image,
    pos=(sheet_image.get_width() / 2, sheet_image.get_height() / 2),
    origin=Sprite.ORIGIN_CENTER,
  )]

  price_image = assets.ttf["english"].render(str(item.value))
  price_image = stroke(price_image, BLACK)
  if not selected:
    if item.value not in cache:
      cache[item.value] = darken_image(price_image)
    price_image = cache[item.value]
  sprites += [price_sprite := Sprite(
    image=price_image,
    pos=(item_sprite.rect.right - 6, item_sprite.rect.bottom + 2),
    origin=Sprite.ORIGIN_BOTTOMLEFT,
    layer="pricetag",
  )]

  return sprites

class ItemGrid:
  def __init__(grid, items, cols, height=0):
    grid.items = items
    grid.cols = cols
    grid.height = height or (ceil(len(grid.items) / grid.cols) // 1 * ITEM_HEIGHT)
    grid.selection = 0
    grid.cursor_anim = CursorAnim(period=30)
    grid.cursor_drawn = grid.project_index(0)
    grid.hand_drawn = grid.project_index(0)
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

  def view(grid, focused=False):
    grid.scroll_drawn += (grid.scroll - grid.scroll_drawn) / 8
    scroll_offset = (0, grid.scroll_drawn * -ITEM_HEIGHT)
    return Sprite.move_all(
      grid.view_items(focused) + grid.view_cursor(focused),
      scroll_offset
    )

  def view_items(grid, focused=None):
    sprites = []
    item_x = 0
    item_y = 0
    for i, item in enumerate(grid.items):
      item_view = view_itemcell(item, selected=focused or i == grid.selection)
      Sprite.move_all(item_view, (item_x, item_y))
      sprites += item_view
      item_x += ITEM_WIDTH
      if item_x >= ITEM_WIDTH * GRID_COLS:
        item_x = 0
        item_y += ITEM_HEIGHT
    return sprites

  def view_cursor(grid, focused=True):
    sprites = []
    selection_col, selection_row = grid.project_index(grid.selection)

    grid.cursor_anim.update()
    cursor_image = assets.sprites["buy_cursor"][int(grid.cursor_anim.time % 30 / 30 * len(assets.sprites["buy_cursor"]))]
    cursor_col, cursor_row = grid.cursor_drawn
    cursor_col += (selection_col - cursor_col) / 2
    cursor_row += (selection_row - cursor_row) / 2
    grid.cursor_drawn = (cursor_col, cursor_row)
    sprites += [Sprite(
      image=cursor_image,
      pos=vector.add(
        (cursor_col * ITEM_WIDTH, cursor_row * ITEM_HEIGHT),
        (cursor_image.get_width() / 2, cursor_image.get_height() / 2)
      ),
      origin=Sprite.ORIGIN_CENTER,
      layer="cursor"
    )]

    if focused:
      hand_image = assets.sprites["hand"]
      hand_col, hand_row = grid.hand_drawn
      hand_col += (selection_col - hand_col) / 4
      hand_row += (selection_row - hand_row) / 4
      grid.hand_drawn = (hand_col, hand_row)
      sprites += [Sprite(
        image=hand_image,
        pos=(
          hand_col * ITEM_WIDTH + 8 + grid.cursor_anim.pos * 2,
          (hand_row + 0.5) * ITEM_HEIGHT
        ),
        origin=Sprite.ORIGIN_RIGHT,
        flip=(True, False),
        layer="hand"
      )]

    return sprites

class ItemTextBox:
  def __init__(box, width):
    box.width = width
    box.textbox = TextBox(
      font="normal",
      size=(
        width - TEXTBOX_LPADDING - 16 - TEXTBOX_ICON_MARGIN - TEXTBOX_RPADDING - 8,
        assets.ttf["normal"].height() * 2 + 4
      ),
      color=WHITE
    )
    box.item = None

  def reload(box, item):
    box.item = item
    box.textbox.print(item.desc)
    box.cache_rarity = None

  def view(box):
    sprites = []
    item = box.item
    icon_image = item().render()

    if "cache_bg" not in dir(box):
      box.cache_bg = Box(
        sprite_prefix="buy_textbox",
        size=(box.width, (0
          + TEXTBOX_YPADDING
          + icon_image.get_height() // 2
          + assets.ttf["normal"].height() // 2
          + TEXTBOX_TITLE_MARGIN
          + assets.ttf["normal"].height()
          + 4
          + assets.ttf["normal"].height()
          + (icon_image.get_height() // 2 - assets.ttf["normal"].height() // 2)
          + TEXTBOX_DESC_MARGIN
          + TEXTBOX_YPADDING
        )),
      ).render()
      # box.cache_bg = shadow(box.cache_bg, BLACK, i=2)
    sprites.append(box_sprite := Sprite(
      image=box.cache_bg,
    ))

    icon_image = stroke(icon_image, WHITE)
    sprites.append(icon_sprite := Sprite(
      image=icon_image,
      pos=(TEXTBOX_LPADDING, TEXTBOX_YPADDING),
    ))

    title_image = assets.ttf["english"].render(item.name, color=YELLOW)
    title_image = outline(title_image, BLACK)
    sprites.append(title_sprite := Sprite(
      image=title_image,
      pos=(icon_sprite.rect.right + TEXTBOX_ICON_MARGIN, icon_sprite.rect.centery + 1),
      origin=Sprite.ORIGIN_LEFT
    ))

    price_image = assets.ttf["english"].render(f"{item.value}G")
    price_image = outline(price_image, BLACK)
    sprites.append(price_sprite := Sprite(
      image=price_image,
      pos=(
        box_sprite.image.get_width() - TEXTBOX_LPADDING,
        title_sprite.rect.top
      ),
      origin=Sprite.ORIGIN_TOPRIGHT,
    ))

    desc_image = box.textbox.render()
    desc_image = shadow(desc_image, BLACK)
    sprites.append(desc_sprite := Sprite(
      image=desc_image,
      pos=(
        title_sprite.x,
        title_sprite.rect.bottom + TEXTBOX_TITLE_MARGIN
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

class CounterContext(Context):
  MIN_VALUE = 1
  MAX_VALUE = 9

  def __init__(counter, value=1, on_change=None, *args, **kwargs):
    super().__init__(*args, **kwargs)
    counter.value = 1
    counter.pressed_up = False
    counter.pressed_down = False
    counter.bounce_anim = SineAnim(period=30)
    counter.on_change = on_change

  def handle_press(counter, button):
    press_time = keyboard.get_state(button) + gamepad.get_state(button)
    if not (press_time == 1
    or press_time >= 30 and press_time % 2):
      return False

    if button in (pygame.K_UP, gamepad.controls.UP):
      counter.pressed_up = True
      return counter.handle_increment()

    if button in (pygame.K_DOWN, gamepad.controls.DOWN):
      counter.pressed_down = True
      return counter.handle_decrement()

    if button in (pygame.K_ESCAPE, pygame.K_BACKSPACE, gamepad.controls.cancel):
      return counter.close()

  def handle_release(counter, button):
    if button in (pygame.K_UP, gamepad.controls.UP):
      counter.pressed_up = False

    if button in (pygame.K_DOWN, gamepad.controls.DOWN):
      counter.pressed_down = False

  @property
  def can_increment(counter):
    return counter.value < counter.MAX_VALUE

  @property
  def can_decrement(counter):
    return counter.value > counter.MIN_VALUE

  def handle_increment(counter):
    if counter.can_increment:
      counter.value += 1
      counter.on_change(counter.value)
      return True
    else:
      return False

  def handle_decrement(counter):
    if counter.can_decrement:
      counter.value -= 1
      counter.on_change(counter.value)
      return True
    else:
      return False

  def update(counter):
    counter.bounce_anim.update()

  def view(counter):
    sprites = []
    sprites += [Sprite(
      image=assets.sprites["buy_quantity_circle"],
      pos=(0, 0),
      origin=Sprite.ORIGIN_CENTER,
      layer="counter",
    )]

    value_color = WHITE if counter.can_increment else GOLD
    value_image = assets.ttf["english"].render(str(counter.value), color=value_color)
    value_image = outline(value_image, BLACK)
    sprites += [Sprite(
      image=value_image,
      pos=(0, 1),
      origin=Sprite.ORIGIN_CENTER,
      layer="counter",
    )]

    uarrow_image = assets.sprites["buy_quantity_uarrow"]
    uarrow_y = -assets.sprites["buy_quantity_circle"].get_height() / 2
    if counter.pressed_up:
      uarrow_image = replace_color(uarrow_image, BROWN, GOLD)
    elif counter.can_increment:
      uarrow_y -= counter.bounce_anim.pos
    else:
      uarrow_image = replace_color(uarrow_image, BROWN, DARKBROWN)
    sprites += [Sprite(
      image=uarrow_image,
      pos=(0, uarrow_y),
      origin=Sprite.ORIGIN_BOTTOM,
      layer="counter",
    )]

    darrow_image = assets.sprites["buy_quantity_darrow"]
    darrow_y = assets.sprites["buy_quantity_circle"].get_height() / 2 + 2
    if counter.pressed_down:
      darrow_image = replace_color(darrow_image, BROWN, GOLD)
    elif counter.can_decrement:
      darrow_y += counter.bounce_anim.pos
    else:
      darrow_image = replace_color(darrow_image, BROWN, DARKBROWN)
    sprites += [Sprite(
      image=darrow_image,
      pos=(0, darrow_y),
      origin=Sprite.ORIGIN_TOP,
      layer="counter",
    )]

    return sprites

class GridContext(Context):
  def __init__(
    ctx,
    items,
    height=0,
    on_change_item=None,
    on_select_item=None,
    on_deselect_item=None,
    on_change_quantity=None,
    *args, **kwargs
  ):
    super().__init__(*args, **kwargs)
    ctx.height = height
    ctx.itemgrid = ItemGrid(
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
    ctx.cursor = (0, 0)
    ctx.on_select_item = on_select_item
    ctx.on_deselect_item = on_deselect_item
    ctx.on_change_item = on_change_item
    on_change_item and on_change_item(ctx.item)
    ctx.on_change_quantity = on_change_quantity

  @property
  def item(ctx):
    return ctx.itemgrid.item

  def handle_press(ctx, button):
    if ctx.child:
      return super().handle_press(button)

    if keyboard.get_state(button) + gamepad.get_state(button) > 1:
      return

    if button in keyboard.ARROW_DELTAS:
      delta = keyboard.ARROW_DELTAS[button]
      return ctx.handle_move(delta)

    if button in (pygame.K_RETURN, gamepad.controls.confirm):
      return ctx.handle_select()

  def handle_move(ctx, delta):
    target_cell = vector.add(ctx.cursor, delta)
    selected = ctx.itemgrid.select(cell=target_cell)
    if selected:
      ctx.cursor = target_cell
      ctx.on_change_item and ctx.on_change_item(ctx.item)
    return selected

  def handle_select(ctx):
    ctx.on_select_item()
    ctx.open(CounterContext(
      on_change=ctx.on_change_quantity
    ), on_close=ctx.on_deselect_item)
    return True

  def view(ctx):
    itemgrid_view = ctx.itemgrid.view(focused=not ctx.child)
    itemgrid_bounds = Sprite.bounds_all(itemgrid_view)

    box_x = WINDOW_WIDTH - ctx.itemgrid.width + (ITEM_WIDTH - assets.sprites["buy_itemsheet"].get_width()) - BOX_XMARGIN
    box_y = BOX_YMARGIN
    return Sprite.move_all(
      sprites=itemgrid_view,
      offset=vector.add((box_x, box_y), (ITEMGRID_XPADDING, ITEMGRID_YPADDING))
    ) + super().view()

class BuyContext(Context):
  def __init__(ctx, hud=None, *args, **kwargs):
    super().__init__(*args, **kwargs)
    ctx.textbox = ItemTextBox(width=160 + (28 if ENABLED_ITEM_RARITY_STARS else 0))
    ctx.gridctx = GridContext(
      items=[resolve_item(i) for i in ITEMS],
      height=108,
      on_change_item=ctx.textbox.reload,
      on_select_item=ctx.handle_select,
      on_deselect_item=ctx.handle_deselect,
      on_change_quantity=ctx.handle_change_quantity,
    )
    ctx.bg = Bg(
      size=(WINDOW_WIDTH, BG_HEIGHT),
      sprite_id="buy_bgtile",
    )
    ctx.tag = ShopTag("general_store")
    ctx.card = Card("buy")
    ctx.hud = hud or Hud(party=[Knight()])
    ctx.goldbubble = GoldBubble(gold=200)
    ctx.textbubble = TextBubble(width=120)
    ctx.portrait = HusbandPortrait()

  def enter(ctx):
    ctx.open(child=ctx.gridctx)
    ctx.textbubble.print("WHAT'S GOT YER EYE?")

  def handle_select(ctx):
    ctx.textbubble.print("HOW MANY YOU LOOKIN TO BUY?")
    ctx.goldbubble.delta = -ctx.gridctx.item.value # use event data?

  def handle_deselect(ctx):
    ctx.textbubble.print("ANYTHING ELSE?")
    ctx.goldbubble.delta = 0 # use event data?

  def handle_change_quantity(ctx, quantity):
    ctx.goldbubble.delta = -ctx.gridctx.item.value * quantity

  def view(ctx):
    sprites = []

    sprites += [bg_mask := SpriteMask(
      pos=(0, BG_Y),
      size=ctx.bg.size,
      children=ctx.bg.view(),
      key="grid_bg"
    )]

    grid_view = super().view()
    sprites += grid_view

    box_sprite = next((s for s in grid_view if s.key == "box"), None)
    sprites += Sprite.move_all(
      sprites=ctx.textbox.view(),
      offset=(WINDOW_WIDTH - BOX_XMARGIN, WINDOW_HEIGHT - 8),
      origin=Sprite.ORIGIN_BOTTOMRIGHT,
      layer="textbox",
    )

    topbar_image = Surface((WINDOW_WIDTH, BG_Y))
    bottombar_image = Surface((WINDOW_WIDTH, WINDOW_HEIGHT - BG_Y - BG_HEIGHT))
    sprites += [Sprite(
      image=topbar_image,
      pos=(0, 0),
      layer="bar",
    ), Sprite(
      image=bottombar_image,
      pos=(0, WINDOW_HEIGHT),
      origin=Sprite.ORIGIN_BOTTOMLEFT,
      layer="bar",
    )]

    sprites += [portrait_sprite := Sprite(
      image=ctx.portrait.render(),
      pos=(WINDOW_WIDTH / 2 - 48, BG_Y + BG_HEIGHT),
      origin=Sprite.ORIGIN_BOTTOM,
      layer="portrait",
    )]

    textbubble_view = ctx.textbubble.view()
    sprites += Sprite.move_all(
      sprites=textbubble_view,
      offset=portrait_sprite.rect.center,
      layer="textbox",
    )

    counter_view = [s for s in grid_view if s.layer == "counter"]
    sprites += Sprite.move_all(
      sprites=counter_view,
      offset=vector.add(
        portrait_sprite.rect.center,
        (-8, 0)
      )
    )

    sprites += [hud_sprite := Sprite(
      image=ctx.hud.render(),
      pos=(BOX_XMARGIN, WINDOW_HEIGHT - 8),
      origin=Sprite.ORIGIN_BOTTOMLEFT,
      layer="hud",
    )]

    sprites += Sprite.move_all(
      sprites=ctx.goldbubble.view(),
      offset=(hud_sprite.rect.right + 4, hud_sprite.rect.centery),
      layer="hud",
    )

    if "cache_title" not in dir(ctx):
      ctx.cache_title = assets.ttf["roman_large"].render("Buy items")
      ctx.cache_title = outline(ctx.cache_title, BROWN)
      ctx.cache_title = shadow(ctx.cache_title, BLACK, i=2)
    sprites += [title_sprite := Sprite(
      image=ctx.cache_title,
      pos=(24, 16 + 1),
      origin=Sprite.ORIGIN_LEFT,
      layer="hud",
    )]

    LAYERS = ["bg", "item", "cursor", "pricetag", "hand", "bar", "portrait", "textbox", "counter", "hud"]
    sprites.sort(key=lambda s: (
      LAYERS.index(s.layer) + 1 if s.layer in LAYERS else 0
    ))

    return sprites
