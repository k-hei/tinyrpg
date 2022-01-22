import sys
from contexts.app import App
from game.context import GameContext
from contexts.explore.manifest import manifest_room
from contexts.explore.roomdata import load_room
from dungeon.floors.floor1 import Floor1
from savedata import load

room_data = load_room("rooms/", "shrine")
stage = manifest_room(room_data)

savedata = load("src/data-debug.json", *sys.argv[1:])
savedata.place = "dungeon"
App(
  title="explore context demo",
  context=GameContext(
    data=savedata,
    floor=Floor1,
    # stage=stage,
  )
).init()
