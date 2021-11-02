from contexts.app import App
from town.topview.context import TopViewContext
from town.areas.store import StoreArea
from game.data import GameData
from cores.knight import Knight

App(title="general store demo",
  context=TopViewContext(
    area=StoreArea,
    store=GameData(party=[Knight()])
  )
).init()
