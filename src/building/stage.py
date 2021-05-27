class Stage:
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
