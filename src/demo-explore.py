import sys
from contexts.app import App
from game.context import GameContext
from contexts.explore.manifest import manifest_room
from contexts.explore.roomdata import load_room
from dungeon.floors.debugfloor import DebugFloor
from savedata import load

room_data = load_room("rooms/", "shrine")
stage = manifest_room(room_data)

savedata = load("src/data-debug.json", *sys.argv[1:])
savedata.place = "dungeon"
App(
  title="explore context demo",
  context=GameContext(
    data=savedata,
    # floor=DebugFloor,
    stage=stage,
  )
).init()
