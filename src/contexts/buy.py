from pygame import Surface, SRCALPHA
from contexts import Context
from savedata.resolve import resolve_item
import assets
from lib.sprite import Sprite
from lib.filters import shadow_lite as shadow
from colors.palette import WHITE, CYAN, CORAL
from config import WINDOW_SIZE

GRID_COLS = 3
ITEM_WIDTH = 32
ITEM_HEIGHT = 32

def view_item_sticky(item, price=0):
  sticky_image = assets.sprites["buy_sticky"]
  item_image = item().render()
  return [
    Sprite(image=shadow(sticky_image, CORAL, i=2)),
    Sprite(
      image=item_image,
      pos=(sticky_image.get_width() / 2, sticky_image.get_height() / 2 + 1),
      origin=Sprite.ORIGIN_CENTER,
    ),
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
      item_view = view_item_sticky(item)
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
