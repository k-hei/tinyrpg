from contexts.app import App
from town.sideview import SideViewContext
from town.areas.central import CentralArea

App(title="town side view demo",
  context=SideViewContext(area=CentralArea)
).init()
