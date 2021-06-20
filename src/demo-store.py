from contexts.app import App
from town.topview import TopViewContext
from town.areas.store import StoreArea

App(title="general store demo",
  context=TopViewContext(area=StoreArea)
).init()
