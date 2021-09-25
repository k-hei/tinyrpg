import sys
import json
from os.path import splitext, basename
from random import choice

from contexts.app import App
from game.context import GameContext
from dungeon.roomdata import RoomData
from dungeon.room import Blob as Room
from savedata import load

from dungeon.gen.manifest import manifest_stage_from_room

argc = len(sys.argv)
if argc != 2:
  print("usage: demo-room.py rooms/example.json")
  exit()

room_path = sys.argv[1]
room_id = splitext(basename(room_path))[0]
room_file = open(room_path, "r")
room_data = json.loads(room_file.read())
room_file.close()

if type(room_data) is list:
  room_data = choice(room_data)
room_data = RoomData(**room_data)
room = Room(data=room_data)
stage = manifest_stage_from_room(room)

App(
  title=f"{room_id} demo",
  context=GameContext(
    data=load("src/data-debug.json"),
    stage=stage
  )
).init()
