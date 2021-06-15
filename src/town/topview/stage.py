from dataclasses import dataclass
from config import TILE_SIZE
from town.topview.door import Door

@dataclass
class Tile:
  solid: bool = False
  halfsolid: bool = False
  door: bool = False

  def is_solid(tile):
    return tile and tile.solid

  def is_halfsolid(tile):
    return tile and tile.halfsolid

  def is_door(tile):
    return tile and tile.door

@dataclass
class Link:
  cell: tuple[int, int]
  direction: tuple[int, int]

class Stage:
  FLOOR = Tile(solid=False)
  WALL = Tile(solid=True)
  HALF_WALL = Tile(halfsolid=True)
  scale = 32

  def parse_char(char):
    if char == ".": return Stage.FLOOR
    if char == "#": return Stage.WALL
    if char == "'": return Stage.HALF_WALL

  def __init__(stage, layout, elems):
    stage.matrix = []
    stage.elems = []
    for y, row in enumerate(layout):
      stage.matrix.append([])
      for x, char in enumerate(row):
        if char in elems:
          tile = Stage.FLOOR
          elem = elems[char]
          if callable(elem):
            elem = elem()
          stage.spawn_elem_at((x, y), elem)
        else:
          tile = Stage.parse_char(char)
        stage.matrix[y].append(tile)

  def get_width(stage):
    return len(stage.matrix[0]) if len(stage.matrix) else 0

  def get_height(stage):
    return len(stage.matrix)

  def get_size(stage):
    return (stage.get_width(), stage.get_height())

  def contains(stage, cell):
    x, y = cell
    width, height = stage.get_size()
    return x >= 0 and y >= 0 and x < width and y < height

  def get_tile_at(stage, cell):
    x, y = cell
    return stage.matrix[y][x] if stage.contains(cell) else None

  def set_tile_at(stage, cell, tile):
    if not stage.contains(cell):
      return
    x, y = cell
    stage.matrix[y][x] = tile

  def spawn_elem_at(stage, cell, elem):
    x, y = cell
    elem.spawn((
      (x + 0.5) * stage.scale,
      (y + 0.5) * stage.scale
    ))
    stage.elems.append(elem)
