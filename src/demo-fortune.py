from contexts.app import App
from town.topview import TopViewContext
from town.areas.fortune import FortuneArea
from cores.knight import KnightCore

App(title="fortune house demo",
  context=TopViewContext(
    area=FortuneArea,
    hero=KnightCore()
  )
).init()
