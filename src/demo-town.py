from contexts.app import App
from contexts.game import GameContext
from cores.knight import KnightCore

App(title="town demo",
  context=GameContext(KnightCore())
).init()
