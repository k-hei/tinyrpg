from contexts.app import App
from contexts.nameentry import NameEntryContext

menu = NameEntryContext()
demo = App("name entry demo")
demo.init(menu)
demo.loop()
