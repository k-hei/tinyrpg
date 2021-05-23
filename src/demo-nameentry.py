from contexts.app import App
from contexts.nameentry import NameEntryContext
from cores.knight import KnightCore

App(title="name entry demo",
  context=NameEntryContext(char=KnightCore())
).init()
