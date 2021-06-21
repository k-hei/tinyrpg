from contexts.app import App
from contexts.game import GameContext
import savedata

App(title="town demo",
  context=GameContext(savedata.load("src/data0.json"))
).init()
