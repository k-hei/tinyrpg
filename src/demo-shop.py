from contexts.app import App
from town.areas.store.context import StoreContext

App(
  title="shop demo",
  context=StoreContext()
).init()
