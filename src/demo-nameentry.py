from contexts.app import App
from contexts.nameentry import NameEntryContext
from cores.mage import MageCore

App(title="name entry demo",
  context=NameEntryContext(
    char=MageCore(),
    on_close=lambda name: print(name)
  )
).init()
