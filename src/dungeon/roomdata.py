import json
from os import listdir
from os.path import join, splitext
from dataclasses import dataclass, field
from dungeon.stage import Stage
from resolve.hook import resolve_hook
from config import ROOMS_PATH

rooms = {}

def load_room(path, key):
  try:
    room_file = open(join(path, key) + ".json", "r")
    room_data = json.loads(room_file.read())
  except FileNotFoundError:
    room_file = None
    print(f"FileNotFoundError: Failed to find file {key}.json at {path}")
    return None
  finally:
    room_file and room_file.close()
  return room_data

def load_rooms():
  for f in listdir(ROOMS_PATH):
    room_id, _ = splitext(f)
    rooms[room_id.replace("-", "_")] = load_room(path=ROOMS_PATH, key=room_id)

def resolve_tile(char):
  if char == "#": return Stage.WALL
  if char == ".": return Stage.FLOOR
  if char == ",": return Stage.HALLWAY
  if char == ">": return Stage.STAIRS_DOWN
  if char == "<": return Stage.STAIRS_UP
  if char == "-": return Stage.STAIRS
  if char == "/": return Stage.STAIRS_RIGHT
  if char == "\\": return Stage.STAIRS_LEFT
  if char == "=": return Stage.LADDER
  if char == "O": return Stage.OASIS
  if char == "V": return Stage.OASIS_STAIRS
  if char == "·": return Stage.FLOOR_ELEV
  if char == "E": return Stage.STAIRS_EXIT
  return Stage.PIT

@dataclass
class RoomData:
  size: tuple[int, int] = None                              # default: generated interior
  tiles: list[int] = field(default_factory=lambda: [])      # default: generated interior
  elems: list[list] = field(default_factory=lambda: [])     # default: no elements
  spawns_vases: bool = False                                # default: no vases spawn
  spawns_enemies: bool = False                              # default: no enemies spawn
  edges: list[list] = field(default_factory=lambda: [])     # default: all edges
  doors: str = "Door"                                       # default: standard door
  secret: bool = False                                      # default: arbitrary (could use ternary?)
  degree: int = 0                                           # default: arbitrary degree
  hooks: dict[str, str] = field(default_factory=lambda: {}) # default: no hooks

  def __post_init__(roomdata):
    if roomdata.tiles and type(roomdata.tiles[0]) is str:
      roomdata.size = (len(roomdata.tiles[0]), len(roomdata.tiles))
      roomdata.tiles = [Stage.TILE_ORDER.index(resolve_tile(c)) for s in roomdata.tiles for c in s]
    roomdata.hooks = { k: resolve_hook(h) if type(h) is str else h for k, h in roomdata.hooks.items() }

  def extract_cells(roomdata):
    cells = []
    width, height = roomdata.size
    for y in range(height):
      for x in range(width):
        if roomdata.tiles[y * width + x] != 1:
          cells.append((x, y))
    return cells
