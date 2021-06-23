from contexts.app import App
from contexts.game import GameContext
import savedata

App(title="town demo",
  context=GameContext(savedata.load("src/data-town.json"))
).init()
