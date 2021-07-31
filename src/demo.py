from contexts.app import App
from contexts.game import GameContext
import savedata

App(title="tinyrpg demo",
  context=GameContext(savedata.load("src/data01.json"))
).init()
