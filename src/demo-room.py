import sys
import json
from os.path import splitext, basename
from random import choice
from resolve.elem import resolve_elem
from dungeon.decoder import decode_elem

from contexts.app import App
from game.context import GameContext
from dungeon.roomdata import RoomData
from dungeon.room import Blob as Room
from dungeon.stage import Stage
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
stage.rooms = [room]

for y in range(room.height):
  for x in range(room.width):
    tile_id = room.data.tiles[y * room.width + x]
    tile = Stage.TILE_ORDER[tile_id]
    stage.set_tile_at((x + 1, y + 1), tile)

for elem_cell, elem_name, *elem_props in room.data.elems:
  elem_props = elem_props[0] if elem_props else {}
  elem = decode_elem(elem_cell, elem_name, elem_props)
  stage.spawn_elem_at(tuple([x + 1 for x in elem_cell]), elem)

for i in range(max(1, room.data.degree)):
  door_cell = tuple([x + 1 for x in room.data.edges[i]])
  door = resolve_elem(room.data.doors)()
  stage.set_tile_at(door_cell, Stage.HALLWAY)
  stage.spawn_elem_at(door_cell, door)
  if not stage.entrance:
    stage.entrance = door_cell
    door.open()

room.on_place(stage)

App(
  title=f"{room_id} demo",
  context=GameContext(
    data=load("src/data-debug.json"),
    stage=stage
  )
).init()
