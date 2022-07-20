import json
from os import listdir
from os.path import join, splitext
from dataclasses import dataclass, field
from pygame import Rect
from lib.grid import Grid

from locations.tileset import Tileset
from contexts.explore.tile_matrix import TileMatrix
from resolve.hook import resolve_hook
from resolve.tileset import resolve_tileset
from config import ROOMS_PATH

rooms = {}

def load_room(path, key):
  with open(join(path, key) + ".json", mode="r", encoding="utf-8") as room_file:
    room_buffer = room_file.read()
    room_data = json.loads(room_buffer)
    return ([RoomData(**d, key=f"{key}{i}") for i, d in enumerate(room_data)]
      if isinstance(room_data, list)
      else RoomData(**room_data, key=key))

def load_rooms():
  if rooms:
    return False
  for f in listdir(ROOMS_PATH):
    room_id, _ = splitext(f)
    room_data = load_room(path=ROOMS_PATH, key=room_id)
    rooms[room_id.replace("-", "_")] = room_data
  return True


@dataclass
class RoomPort:
  x: int = None
  y: int = None
  direction: tuple[int, int] = None

  def __post_init__(port):
    port.direction = tuple(port.direction)

  @property
  def cell(port):
    return (port.x, port.y)

@dataclass
class RoomData:
  """
  Models an in-game top-down area.
  """

  key: str = None
  name: str = None
  bg: tuple[str, str] = ("tileset", "default")
  size: tuple[int, int] = None                              # default: generated size
  tiles: list[int] = field(default_factory=list)            # default: generated shape
  elems: list[list] = field(default_factory=list)           # default: no elements
  rooms: list[list] = field(default_factory=list)           # default: no subrooms
  edges: list[list] = field(default_factory=list)           # default: all edges
  ports: dict[str, RoomPort] = field(default_factory=dict)  # default: all edges
  doors: str = "Door"                                       # default: generic door
  secret: bool = None                                       # default: arbitrary secrecy
  degree: int = 0                                           # default: arbitrary degree
  terrain: bool = None                                      # default: true when tiles var is false
  items: bool = False                                       # default: no vases spawn
  enemies: bool = False                                     # default: no enemies spawn
  hooks: dict[str, str] = field(default_factory=lambda: {}) # default: no hooks
  collision_whitelist: list = field(default_factory=list)   # default: no collision whitelist

  def __hash__(roomdata):
    return hash(roomdata.key)

  def __str__(area):
    return str(area.key)

  def __post_init__(roomdata):
    if not isinstance(roomdata.bg, type) or not issubclass(roomdata.bg, Tileset):
      bg_type, bg_id = roomdata.bg
      if bg_type == "tileset":
        tileset = resolve_tileset(bg_id)
      else:
        tileset = resolve_tileset("default")
      roomdata.bg = tileset

    if not roomdata.tiles:
      roomdata.tiles = TileMatrix(layers=[Grid(size=roomdata.size)])

    if roomdata.tiles and not isinstance(roomdata.tiles, TileMatrix):
      if isinstance(roomdata.tiles[0], str):
        # string format
        roomdata.size = (len(roomdata.tiles[0]), len(roomdata.tiles))
        roomdata.tiles = TileMatrix(layers=[Grid(
          size=tuple(roomdata.size),
          data=[tileset.mappings[c] if c in tileset.mappings else None for s in roomdata.tiles for c in s]
        )])
      elif isinstance(roomdata.tiles[0], list):
        # multi-layer format
        roomdata.tiles = TileMatrix(layers=[Grid(
          size=tuple(roomdata.size),
          data=layer,
        ) for layer in roomdata.tiles])
      else:
        # single-layer format
        roomdata.tiles = TileMatrix(layers=[Grid(
          size=tuple(roomdata.size),
          data=roomdata.tiles,
        )])

    if not roomdata.tiles and roomdata.terrain is None:
      roomdata.terrain = True

    roomdata.hooks = { k: resolve_hook(h) if type(h) is str else h for k, h in roomdata.hooks.items() }
    roomdata.ports = { n: RoomPort(**l) for n, l in roomdata.ports.items() }

    roomdata.collision_whitelist = [Rect(*r) for r in roomdata.collision_whitelist]

  def extract_cells(roomdata):
    return [c for c, t in roomdata.tiles.enumerate()]
    # TODO: use tileset to determine solidity (how do image bgs work?)
    # if not issubclass(t, tileset.Wall)]
