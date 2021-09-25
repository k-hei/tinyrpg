import sys
import json
from os.path import splitext, basename
from random import choice
from lib.cell import add as add_vector
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
room.origin = (1, 2)
stage = Stage((room.width + 2, room.height + 3))
stage.fill(Stage.WALL)
stage.rooms = [room]

for y in range(room.height):
  for x in range(room.width):
    tile_id = room.data.tiles[y * room.width + x]
    tile = Stage.TILE_ORDER[tile_id]
    stage.set_tile_at(add_vector(room.origin, (x, y)), tile)

for elem_cell, elem_name, *elem_props in room.data.elems:
  elem_props = elem_props[0] if elem_props else {}
  elem = decode_elem(elem_cell, elem_name, elem_props)
  stage.spawn_elem_at(add_vector(room.origin, elem_cell), elem)

door_cell = None
if room.data.edges:
  for i in range(max(1, room.data.degree)):
    door_cell = add_vector(room.origin, room.data.edges[-i])
    door = resolve_elem(room.data.doors)()
    stage.set_tile_at(door_cell, Stage.HALLWAY)
    stage.spawn_elem_at(door_cell, door)

if door_cell:
  stage.entrance = door_cell
  door.open()
else:
  stage.entrance = stage.find_tile(stage.STAIRS_EXIT)

room.on_place(stage)

App(
  title=f"{room_id} demo",
  context=GameContext(
    data=load("src/data-debug.json"),
    stage=stage
  )
).init()
