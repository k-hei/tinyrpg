class Grid:
  def __init__(grid, size, data=None):
    grid._size = size
    grid.data = data or [None] * (grid.width * grid.height)

  @property
  def size(grid):
    return grid._size

  @property
  def width(grid):
    return grid.size[0]

  @property
  def height(grid):
    return grid.size[1]

  def __contains__(grid, cell):
    x, y = cell
    return (x >= 0
      and y >= 0
      and x < grid.width
      and y < grid.height)

  def __getitem__(grid, cell):
    cell_index = grid.index(cell)
    if cell_index == -1:
      raise IndexError("grid index out of range")
    return grid.data[cell_index]

  def __setitem__(grid, cell, data):
    cell_index = grid.index(cell)
    if cell_index == -1:
      raise IndexError("grid assignment index out of range")
    grid.data[cell_index] = data

  def index(grid, cell):
    if cell not in grid:
      return -1

    x, y = cell
    return int(y) * grid.width + int(x)

  def enumerate(grid):
    return [((x, y), grid[x, y]) for y in range(grid.height) for x in range(grid.width)]

  def fill(grid, data):
    for cell, _ in grid.enumerate():
      grid[cell] = data
