import sys
from importlib import import_module
from contexts.app import App
import lib.gamepad as gamepad
import game.controls

argc = len(sys.argv)
if argc != 2:
  print("usage: demo-context.py Example")
  exit()

context_name = sys.argv[1]
context_path = "contexts.{}".format(context_name.lower())
context_module = import_module(context_path)
Context = getattr(context_module, context_name + "Context")

gamepad.config(preset=game.controls.TYPE_A)
App(title="{} demo".format(context_name.lower()),
  context=Context()
).init()
