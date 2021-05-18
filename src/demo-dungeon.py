from contexts.app import App
from contexts.game import GameContext
from dungeon import DungeonContext
from cores.knight import KnightCore
from cores.mage import MageCore

App(title="dungeon demo",
  context=GameContext(DungeonContext(), KnightCore(), MageCore())
).init()
