from contexts.app import App
from contexts.game import GameContext

App(title="town demo",
  context=GameContext()
).init()
