from contexts.app import App
from contexts.nameentry import NameEntryContext
from cores.knight import Knight

App(title="name entry demo",
  context=NameEntryContext(char=Knight())
).init()
