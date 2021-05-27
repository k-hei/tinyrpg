from contexts.app import App
from building.context import BuildingContext

App(title="building interior demo",
  context=BuildingContext()
).init()
