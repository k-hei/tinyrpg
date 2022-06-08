from contexts.app import App
from game.context import GameContext
import savedata

game_data = savedata.load("src/data-debug.json")
game_data.place = "town"

App(title="town demo",
  context=GameContext(game_data)
).init()
