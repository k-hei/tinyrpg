from contexts.app import App
from contexts.game import GameContext
from town import TownContext
from cores.knight import KnightCore

App(title="town demo",
  context=GameContext(TownContext(returning=True), KnightCore())
).init()
