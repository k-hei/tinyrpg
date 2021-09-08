from contexts.app import App
from game.context import GameContext
import savedata

App(title="tinyrpg demo", context=GameContext()).init()
