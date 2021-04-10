class Grid:
  def __init__(grid, size):
    (width, height) = size
    grid.size = size
    grid.data = [0] * (width * height)
    grid.actors = []

  def fill(grid, data):
    (width, height) = grid.size
    for i in range(width * height):
      grid.data[i] = data

  def get_cells(grid):
    (width, height) = grid.size
    cells = []
    for y in range(height):
      for x in range(width):
        cells.append((x, y))
    return cells

  def get_at(grid, cell):
    if not grid.contains(cell):
      return None
    width = grid.size[0]
    (x, y) = cell
    return grid.data[y * width + x]

  def set_at(grid, cell, data):
    if not grid.contains(cell):
      return
    width = grid.size[0]
    (x, y) = cell
    grid.data[y * width + x] = data

  def contains(grid, cell):
    (width, height) = grid.size
    (x, y) = cell
    return x >= 0 and y >= 0 and x < width and y < height
