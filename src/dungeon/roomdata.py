from dataclasses import dataclass, field

@dataclass
class RoomData:
  size: tuple[int, int]
  tiles: list[int]
  elems: list[list] = field(default_factory=lambda: [])
  doors: list[list] = field(default_factory=lambda: [])

  def extract_cells(roomdata):
    cells = []
    width, height = roomdata.size
    for y in range(height):
      for x in range(width):
        if roomdata.tiles[y * width + x] == 0:
          cells.append((x, y))
    return cells
