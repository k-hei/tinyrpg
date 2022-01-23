import sys
from importlib import import_module
from contexts.app import App
from game.context import GameContext
from savedata import load

argc = len(sys.argv)
if argc != 2:
  print("usage: demo-floor.py Floor2")
  exit()

floor_name = sys.argv[1]
floor_path = "dungeon.floors.{}".format(floor_name.lower())
floor_module = import_module(floor_path)
generator = getattr(floor_module, floor_name)

savedata = load("src/data-debug.json")
savedata.place = "dungeon"
App(
  title=f"{floor_name.lower()} dungeon demo",
  context=GameContext(
    data=savedata,
    floor=generator,
  )
).init()
