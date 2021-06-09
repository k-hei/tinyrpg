from contexts.app import App
from town.topview import BuildingContext

App(title="building interior demo",
  context=BuildingContext()
).init()
