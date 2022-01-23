import sys
from contexts.app import App
from game.context import GameContext
from contexts.explore.manifest import manifest_room
from contexts.explore.roomdata import load_room
from savedata import load

room_name = sys.argv[1]
room_data = load_room("rooms/", room_name)
stage = manifest_room(room_data)

savedata = load("src/data-debug.json")
savedata.place = "dungeon"
App(
  title="explore context demo",
  context=GameContext(
    data=savedata,
    stage=stage,
  )
).init()
