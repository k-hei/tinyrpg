import sys
from importlib import import_module
from contexts.app import App
from contexts.gen import GenContext
import config

argc = len(sys.argv)
if argc != 2:
  print("usage: demo-gen.py Floor2")
  exit()

floor_name = sys.argv[1]
floor_path = "dungeon.floors.{}".format(floor_name.lower())
floor_module = import_module(floor_path)
generator = getattr(floor_module, floor_name)

App(title="dungeon generator demo",
  context=GenContext(generator, seed=config.SEED)
).init()
