from contexts.app import App
from game.context import GameContext
from savedata import load
from dungeon.features.elevroom import ElevRoom

App(title="elevated room demo",
  context=GameContext(
    savedata=load("src/data00.json"),
    feature=ElevRoom
  )
).init()
