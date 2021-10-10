from pygame import Surface, Rect, SRCALPHA
from pygame.draw import rect as draw_rect
from contexts import Context
from savedata.resolve import resolve_item
import assets
from lib.sprite import Sprite
from lib.filters import stroke, darken_image, shadow_lite as shadow
from colors.palette import BLACK, WHITE, CYAN, CORAL
from config import WINDOW_SIZE

GRID_COLS = 3
ITEM_WIDTH = 32
ITEM_HEIGHT = 32
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
      layer="hud"
    )
  ]

class ItemStickyGrid:
  def __init__(grid, items, cols):
    grid.items = items
    grid.cols = cols

  def view(grid):
    sprites = []
    item_x = 0
    item_y = 0
    for i, item in enumerate(grid.items):
      item_view = view_item_sticky(item, selected=not i)
      Sprite.move_all(item_view, (item_x, item_y))
      sprites += item_view
      item_x += ITEM_WIDTH
      if item_x >= ITEM_WIDTH * GRID_COLS:
        item_x = 0
        item_y += ITEM_HEIGHT
    return sprites

class BuyContext(Context):
  def __init__(ctx, *args, **kwargs):
    super().__init__(*args, **kwargs)
    ctx.itemgrid = ItemStickyGrid(
      cols=GRID_COLS,
      items=[resolve_item(i) for i in ("Potion", "Ankh", "Fish", "Cheese", "Bread", "Antidote", "MusicBox", "Balloon", "Emerald", "Key")],
    )

  def view(ctx):
    bg_image = Surface(WINDOW_SIZE, flags=SRCALPHA)
    bg_image.fill(WHITE)
    bg_view = [Sprite(image=bg_image)]
    itemgrid_view = Sprite.move_all(ctx.itemgrid.view(), (24, 24))
    return bg_view + itemgrid_view
