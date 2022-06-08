from contexts.app import App
from town.sideview.context import SideViewContext
from town.areas.akimor_central import AkimorCentralArea
from game.data import GameData
from savedata import load

App(title="town side view demo",
  context=SideViewContext(
    store=GameData.decode(load("src/data-debug.json")),
    area=AkimorCentralArea
  )
).init()
