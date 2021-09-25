from dataclasses import dataclass, field
from dungeon.stage import Stage

# TODO: move room json loading out of assets so we can resolve hooks post-init

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
  degree: int = 0                                           # default: arbitrary degree
  hooks: dict[str, str] = field(default_factory=lambda: {}) # default: no hooks

  def __post_init__(roomdata):
    if roomdata.tiles and type(roomdata.tiles[0]) is str:
      roomdata.size = (len(roomdata.tiles[0]), len(roomdata.tiles))
      roomdata.tiles = [Stage.TILE_ORDER.index(resolve_tile(c)) for s in roomdata.tiles for c in s]

  def extract_cells(roomdata):
    cells = []
    width, height = roomdata.size
    for y in range(height):
      for x in range(width):
        if roomdata.tiles[y * width + x] != 1:
          cells.append((x, y))
    return cells
