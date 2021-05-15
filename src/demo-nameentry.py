from contexts.nameentry import NameEntryContext
from app import App

menu = NameEntryContext(default_name="Yorgen")
demo = App("name entry demo")
demo.init(menu)
demo.loop()
