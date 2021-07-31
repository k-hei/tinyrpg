from contexts.app import App
from contexts.game import GameContext
import savedata

App(title="tinyrpg demo",
  context=GameContext(savedata.load("src/data00.json"))
).init()
