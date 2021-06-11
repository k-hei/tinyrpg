from contexts.app import App
from town.topview import TopViewContext
from town.areas.fortune import FortuneArea
from cores.knight import KnightCore

App(title="town top-down view demo",
  context=TopViewContext(
    area=FortuneArea,
    hero=KnightCore()
  )
).init()
