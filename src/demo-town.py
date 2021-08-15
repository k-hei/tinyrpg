from contexts.app import App
from game.context import GameContext
import savedata

App(title="town demo",
  context=GameContext(savedata.load("src/data00.json"))
).init()
