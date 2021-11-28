from contexts.app import App
from game.context import GameContext
from contexts.explore.manifest import manifest_stage
from contexts.explore.roomdata import load_room
from cores.knight import Knight
from game.data import GameData

room_data = load_room("rooms/", "debug")
stage = manifest_stage(room_data)

App(
  title="explore context demo",
  context=GameContext(
    data=GameData(party=[Knight()]),
    stage=stage,
  )
).init()
