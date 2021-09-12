from contexts.app import App
from dungeon.gen.context import GenContext

App(title="dungeon generator demo",
  context=GenContext()
).init()
