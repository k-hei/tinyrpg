from contexts.app import App
from town.topview import TopViewContext
from town.areas.store import StoreArea
from cores.knight import KnightCore

App(title="general store demo",
  context=TopViewContext(
    area=StoreArea,
    hero=KnightCore()
  )
).init()
