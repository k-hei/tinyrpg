from dataclasses import dataclass, field

# TODO: move room json loading out of assets so we can resolve hooks post-init

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

  def extract_cells(roomdata):
    cells = []
    width, height = roomdata.size
    for y in range(height):
      for x in range(width):
        if roomdata.tiles[y * width + x] != 1:
          cells.append((x, y))
    return cells
