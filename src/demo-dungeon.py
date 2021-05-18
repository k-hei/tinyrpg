from contexts.app import App
from contexts.game import GameContext
from dungeon import DungeonContext
from cores.knight import KnightCore

App(title="dungeon demo",
  context=GameContext(DungeonContext(), KnightCore())
).init()
