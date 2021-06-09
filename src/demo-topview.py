from contexts.app import App
from town.topview import TopViewContext
from town.areas.shop import ShopArea
from cores.knight import KnightCore

App(title="town top-down view demo",
  context=TopViewContext(
    area=ShopArea,
    hero=KnightCore()
  )
).init()
