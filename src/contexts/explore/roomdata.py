import json
from os import listdir
from os.path import join, splitext
from dataclasses import dataclass, field
from lib.grid import Grid
from resolve.hook import resolve_hook
from resolve.tileset import resolve_tileset
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
  if rooms:
    return False
  for f in listdir(ROOMS_PATH):
    room_id, _ = splitext(f)
    rooms[room_id.replace("-", "_")] = load_room(path=ROOMS_PATH, key=room_id)
  return True

@dataclass
class RoomData:
  bg: tuple[str, str] = ("tileset", "default")
  size: tuple[int, int] = None                              # default: generated size
  tiles: list[int] = field(default_factory=lambda: [])      # default: generated shape
  elems: list[list] = field(default_factory=lambda: [])     # default: no elements
  edges: list[list] = field(default_factory=lambda: [])     # default: all edges
  doors: str = "Door"                                       # default: generic door
  secret: bool = None                                       # default: arbitrary secrecy
  degree: int = 0                                           # default: arbitrary degree
  terrain: bool = None                                      # default: true when tiles var is false
  items: bool = False                                       # default: no vases spawn
  enemies: bool = False                                     # default: no enemies spawn
  hooks: dict[str, str] = field(default_factory=lambda: {}) # default: no hooks

  def __post_init__(roomdata):
    bg_type, bg_id = roomdata.bg
    if bg_type == "tileset":
      tileset = resolve_tileset(bg_id)
    else:
      tileset = resolve_tileset("default")

    if roomdata.tiles and type(roomdata.tiles[0]) is str:
      roomdata.size = (len(roomdata.tiles[0]), len(roomdata.tiles))
      roomdata.tiles = Grid(
        size=roomdata.size,
        data=[tileset[c] for s in roomdata.tiles for c in s]
      )

    if not roomdata.tiles and roomdata.terrain is None:
      roomdata.terrain = True

    roomdata.hooks = { k: resolve_hook(h) if type(h) is str else h for k, h in roomdata.hooks.items() }

  def extract_cells(roomdata):
    cells = []
    width, height = roomdata.size
    for y in range(height):
      for x in range(width):
        i = y * width + x
        if i >= len(roomdata.tiles):
          continue
        if roomdata.tiles[i] != 1:
          cells.append((x, y))
    return cells
