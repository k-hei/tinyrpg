import struct
import base64
import zstd
from lib.bounds import find_bounds
from pygame import Rect
from dungeon.roomdata import RoomData
from dungeon.stage import Stage
import debug

MIN_ROOM_WIDTH = 5
MIN_ROOM_HEIGHT = 5
ID_DOOR = 5
ID_BATTLEDOOR = 6
ID_TREASUREDOOR = 7
ID_RARETREASUREDOOR = 8
ID_PUSHTILE = 19
ID_PUSHBLOCK = 40
ID_PILLAR = 25
ID_COLUMN = 26
ID_WALL = 45
IDS_FLOOR = (1, 2)
IDS_PIT  = (3, 4)
IDS_DOOR = (ID_DOOR, ID_BATTLEDOOR, ID_TREASUREDOOR, ID_RARETREASUREDOOR)
IDS_ELEM = {
  ID_DOOR: "Door",
  ID_BATTLEDOOR: "BattleDoor",
  ID_TREASUREDOOR: "TreasureDoor",
  ID_RARETREASUREDOOR: "RareTreasureDoor",
  ID_PUSHTILE: "PushTile",
  ID_PUSHBLOCK: "PushBlock",
  ID_PILLAR: "Pillar",
  ID_COLUMN: "Column"
}
get_id = Stage.TILE_ORDER.index

def decode(width, height, layers, **kwargs):
  # decode_layers(layers) -> layers_data
  layers_data = [decode_layer(**layer) for layer in layers if layer["type"] == "tilelayer"]

  # find_door_cells(layers_data) -> door_cells
  door_cells = []
  for layer_data in layers_data:
    for y in range(height):
      for x in range(width):
        item_id = layer_data[y * width + x]
        if item_id in IDS_DOOR:
          door_cells.append((x, y))
        print(item_id, end="\t")
      print()
    print()

  # find_room_bounds(layers_data, door_cells) -> bounds
  tile_bounds = find_layer_bounds(width, height, layers_data[0])
  door_bounds = find_bounds(door_cells)
  should_use_doors_width = door_bounds.width >= MIN_ROOM_WIDTH
  should_use_doors_height = door_bounds.height >= MIN_ROOM_HEIGHT
  bounds_left = door_bounds.left if should_use_doors_width else tile_bounds.left
  bounds_top = door_bounds.top if should_use_doors_height else tile_bounds.top
  bounds_width = door_bounds.width if should_use_doors_width else tile_bounds.width
  bounds_height = door_bounds.height if should_use_doors_height else tile_bounds.height
  bounds = Rect(
    (bounds_left, bounds_top),
    (bounds_width, bounds_height)
  )

  # parse_layers_data(layers_data, bounds) -> room
  room = RoomData()
  room.size = bounds.size
  room.tiles = [get_id(Stage.WALL)] * bounds.width * bounds.height
  for layer_data in layers_data:
    for y in range(bounds.top, bounds.bottom):
      for x in range(bounds.left, bounds.right):
        if x < 0 or y < 0 or x >= width or y >= height:
          debug.log(f"WARNING: {(x, y)} out of range")
          continue
        item_id = layer_data[y * width + x]
        parse_item(room, cell=(x - bounds.left, y - bounds.top), item=item_id)
  return room

def decode_layer(width, height, data, **kwargs):
  data_bytes = zstd.loads(base64.b64decode(data))
  data_ids = [data_bytes[i] for i in range(0, len(data_bytes), 4)]
  return data_ids

def find_layer_bounds(width, height, layer):
  cells = []
  for y in range(height):
    for x in range(width):
      item_id = layer[y * width + x]
      if item_id in IDS_FLOOR + IDS_PIT:
        cells.append((x, y))
  return find_bounds(cells)

def parse_item(room, cell, item):
  x, y = cell
  index = y * room.size[0] + x
  if item in IDS_ELEM and item not in IDS_DOOR:
    room.elems.append([[x, y], IDS_ELEM[item]])
  if item in IDS_FLOOR:
    room.tiles[index] = get_id(Stage.FLOOR)
  elif item in IDS_PIT:
    room.tiles[index] = get_id(Stage.PIT)
  elif item >= ID_WALL:
    room.tiles[index] = get_id(Stage.WALL)
  elif item in IDS_DOOR:
    room.tiles[index] = get_id(Stage.HALLWAY)
    room.edges.insert((x, y))
    room.degree += 1
    if item in IDS_ELEM:
      room.doors = IDS_ELEM[item]
