import sys
from importlib import import_module
from contexts.app import App
from game.context import GameContext
from savedata import load

argc = len(sys.argv)
if argc != 2:
  print("usage: demo-feature.py ExampleFeature")
  exit()

feature_name = sys.argv[1]
feature_path = "dungeon.features.{}".format(feature_name.lower())
feature_module = import_module(feature_path)
feature = getattr(feature_module, feature_name)

App(title="{} demo".format(feature_name.lower()),
  context=GameContext(
    savedata=load("src/data00.json"),
    feature=feature
  )
).init()
