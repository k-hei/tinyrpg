from contexts.app import App
from game.context import GameContext
from contexts.explore.manifest import manifest_room
from contexts.explore.roomdata import load_room
from cores.knight import Knight
from dungeon.floors.debugfloor import DebugFloor
from game.data import GameData

room_data = load_room("rooms/", "debug")
stage = manifest_room(room_data)

App(
  title="explore context demo",
  context=GameContext(
    data=GameData(party=[Knight()]),
    floor=DebugFloor,
    # stage=stage,
  )
).init()
