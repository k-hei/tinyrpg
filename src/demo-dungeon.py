from contexts.app import App
from contexts.game import GameContext
from savedata import load
import sys

savedata = load("src/data00.json", *sys.argv[1:])
savedata.place = "dungeon"
App(title="dungeon demo",
  context=GameContext(savedata)
).init()
