from contexts.app import App
from contexts.game import GameContext
from dungeon import DungeonContext
from cores.knight import Knight

App(title="dungeon generator demo",
  context=GameContext(
    DungeonContext(debug=True),
    Knight()
  )
).init()
