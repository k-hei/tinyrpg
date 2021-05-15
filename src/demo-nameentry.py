from app import App
from contexts.nameentry import NameEntryContext

menu = NameEntryContext(default_name="Yorgen")
demo = App("name entry demo")
demo.init(menu)
demo.loop()
