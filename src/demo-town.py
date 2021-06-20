from contexts.app import App
from town import TownContext
import savedata

App(title="town demo",
  context=TownContext()
).init()
