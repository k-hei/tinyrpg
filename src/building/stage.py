from dataclasses import dataclass

@dataclass
class Tile:
  solid: bool = False
  halfsolid: bool = False

  def is_solid(tile):
    return not tile or tile.solid

  def is_halfsolid(tile):
    return not tile or tile.halfsolid

class Stage:
  FLOOR = Tile(solid=False)
  WALL = Tile(solid=True)
  HALF_WALL = Tile(halfsolid=True)

  def parse(matrix):
    parsed_matrix = []
    for y, row in enumerate(matrix):
      parsed_matrix.append([])
      for x, char in enumerate(row):
        parsed_matrix[y].append(Stage.parse_char(char))
    return Stage(parsed_matrix)

  def parse_char(char):
    if char == ".": return Stage.FLOOR
    if char == "#": return Stage.WALL
    if char == "'": return Stage.HALF_WALL

  def __init__(stage, matrix):
    stage.matrix = matrix

  def get_width(stage):
    return len(stage.matrix) and len(stage.matrix[0]) or 0

  def get_height(stage):
    return len(stage.matrix)

  def get_size(stage):
    return (stage.get_width(), stage.get_height())

  def contains(stage, cell):
    x, y = cell
    width, height = stage.get_size()
    return x >= 0 and y >= 0 and x < width and y < height

  def get_tile_at(stage, cell):
    if not stage.contains(cell):
      return None
    x, y = cell
    return stage.matrix[y][x]
