from contexts.app import App
from contexts.nameentry import NameEntryContext

App(title="name entry demo",
  context=NameEntryContext(on_close=lambda name: print(name))
).init()
