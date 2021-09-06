import sys
from importlib import import_module
from contexts.app import App
from game.context import GameContext
from savedata import load

argc = len(sys.argv)
if argc != 2:
  print("usage: demo-arena.py ExampleEnemy")
  exit()

enemy_name = sys.argv[1]
savedata = load("src/data-debug.json", "testdata/data-arena.json")
savedata.dungeon["floors"][0]["elems"].append([[4, 3], enemy_name])

App(title="{} demo".format(enemy_name.lower()),
  context=GameContext(
    data=savedata,
  )
).init()
