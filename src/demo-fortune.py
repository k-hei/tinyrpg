from contexts.app import App
from town.topview import TopViewContext
from town.areas.fortune import FortuneArea

App(title="fortune house demo",
  context=TopViewContext(area=FortuneArea)
).init()
