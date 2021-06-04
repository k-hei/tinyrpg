from contexts.app import App
from contexts.shop import ShopContext
from savedata.resolve import resolve_item

App(
  title="shop demo",
  context=ShopContext()
).init()
