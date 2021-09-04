from contexts.app import App
from game.context import GameContext
from savedata import load
import sys

savedata = load("src/data-debug.json", *sys.argv[1:])
savedata.place = "dungeon"
App(title="dungeon demo",
  context=GameContext(savedata)
).init()
