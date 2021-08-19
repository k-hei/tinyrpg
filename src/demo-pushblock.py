from contexts.app import App
from game.context import GameContext
import savedata

App(title="pushblock demo",
  context=GameContext(savedata.load("src/data00.json", "src/data-pushblock.json"))
).init()
