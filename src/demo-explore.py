import sys
from contexts.app import App
from game.context import GameContext
from contexts.explore.manifest import manifest_room
from contexts.explore.roomdata import load_room
from dungeon.floors.floor2 import Floor2
from savedata import load

room_data = load_room("rooms/", "debug")
stage = manifest_room(room_data)

savedata = load("src/data-debug.json", *sys.argv[1:])
savedata.place = "dungeon"
App(
  title="explore context demo",
  context=GameContext(
    data=savedata,
    floor=Floor2,
    # stage=stage,
  )
).init()
