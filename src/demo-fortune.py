from contexts.app import App
from town.topview.context import TopViewContext
from town.areas.fortune import FortuneArea
from game.data import GameData
from cores.knight import Knight

App(title="fortune house demo",
  context=TopViewContext(
    area=FortuneArea,
    store=GameData(party=[Knight()])
  )
).init()
