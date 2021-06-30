from contexts.app import App
from contexts.game import GameContext
from savedata import load
from dungeon.features.elevroom import ElevRoom

App(title="elevated room demo",
  context=GameContext(
    savedata=load("src/data0.json"),
    feature=ElevRoom
  )
).init()
