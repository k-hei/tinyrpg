import sys
from random import choice

from game.context import GameContext
from contexts.app import App
from contexts.explore.manifest import manifest_room
from contexts.explore.roomdata import load_room
from savedata import load

room_name = sys.argv[1]
room_data = load_room("rooms/", room_name)
if isinstance(room_data, list):
  room_data = choice(room_data)

stage = manifest_room(room_data)

savedata = load("src/data-debug.json")
savedata.place = "dungeon"
App(
  title=f"{room_name} room demo",
  context=GameContext(
    data=savedata,
    stage=stage,
  )
).init()
