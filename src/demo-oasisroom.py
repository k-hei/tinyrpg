from contexts.app import App
from contexts.game import GameContext
from savedata import load
from dungeon.features.oasisroom import OasisRoom

App(title="oasis room demo",
  context=GameContext(
    savedata=load("src/data00.json"),
    feature=OasisRoom
  )
).init()
