import sys
import json
from os.path import splitext, basename
from random import choice
from contexts.app import App
from game.context import GameContext
from dungeon.roomdata import RoomData
from dungeon.room import Blob as Room
from dungeon.stage import Stage
from resolve.elem import resolve_elem
from savedata import load

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
room.origin = (1, 1)
stage = Stage((room.width + 2, room.height + 2))
stage.fill(Stage.WALL)
stage.entrance = tuple([x + 1 for x in room.data.edges[0]])
stage.rooms = [room]
for y in range(room.height):
  for x in range(room.width):
    tile_id = room.data.tiles[y * room.width + x]
    tile = Stage.TILE_ORDER[tile_id]
    stage.set_tile_at((x + 1, y + 1), tile)
stage.set_tile_at(stage.entrance, Stage.HALLWAY)
stage.spawn_elem_at(stage.entrance, door := resolve_elem(room.data.doors)())
door.open()
room.on_place(stage)

App(
  title=f"{room_id} demo",
  context=GameContext(
    data=load("src/data-debug.json"),
    stage=stage
  )
).init()
