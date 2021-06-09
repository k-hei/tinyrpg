from contexts.app import App
from town.sideview import SideViewContext

App(title="town side view demo",
  context=SideViewContext()
).init()
