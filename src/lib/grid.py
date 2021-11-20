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

  def contains(grid, x, y):
    return (
      x >= 0
      and y >= 0
      and x < grid.width
      and y < grid.height
    )

  def get(grid, x, y):
    return grid.data[y * grid.width + x] if grid.contains(x, y) else None

  def set(grid, x, y, data):
    grid.data[y * grid.width + x] = data

  def enumerate(grid):
    return [((x, y), grid.get(x, y)) for y in range(grid.height) for x in range(grid.width)]

  def fill(grid, data):
    for cell, _ in grid.enumerate():
      grid.set(*cell, data)
