from contexts.app import App
from contexts.game import GameContext
from savedata import load

savedata = load("src/data00.json")
savedata.place = "dungeon"
App(title="dungeon demo",
  context=GameContext(savedata)
).init()
