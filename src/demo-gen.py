import sys
from importlib import import_module
from contexts.app import App
from dungeon.gen.context import GenContext

argc = len(sys.argv)
if argc != 2:
  print("usage: demo-floor.py Floor2")
  exit()

floor_name = sys.argv[1]
floor_path = "dungeon.floors.{}".format(floor_name.lower())
floor_module = import_module(floor_path)
floor = getattr(floor_module, floor_name)

App(title="dungeon generator demo",
  context=GenContext(floor)
).init()
