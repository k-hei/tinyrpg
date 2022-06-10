from math import sqrt
import lib.vector as vector

def manhattan(a, b):
  x1, y1 = a
  x2, y2 = b
  return abs(x2 - x1) + abs(y2 - y1)

def is_adjacent(a, b):
  return manhattan(a, b) == 1

def distance(a, b):
  x1, y1 = a
  x2, y2 = b
  dx, dy = x2 - x1, y2 - y1
  return sqrt(dx * dx + dy * dy)

def normal(a, b):
  x1, y1 = a
  x2, y2 = b
  dx, dy = x2 - x1, y2 - y1
  nx, ny = 0, 0
  if dx < 0:
    nx = -1
  elif dx > 0:
    nx = 1
  elif dy < 0:
    ny = -1
  elif dy > 0:
    ny = 1
  return nx, ny

def add(a, b):
  x1, y1 = a
  x2, y2 = b
  return (x1 + x2, y1 + y2)

def subtract(a, b):
  x1, y1 = a
  x2, y2 = b
  return (x1 - x2, y1 - y2)

def is_odd(cell):
  x, y = cell
  return x % 2 == 1 and y % 2 == 1

def upscale(cell, scale):
  return vector.scale(vector.add(cell, (0.5, 0.5)), scale)

def downscale(pos, scale, floor=False):
  cell = vector.subtract(vector.scale(pos, 1 / scale), (0.5, 0.5))
  return vector.floor(cell) if floor else cell

def neighborhood(cell=(0, 0), radius=1, adjacents=True, diagonals=False, inclusive=False, predicate=None):
  if radius == 1:
    x, y = cell
    neighbors = [
      *([cell] if inclusive else []),
      *([
        (x - 1, y),
        (x, y - 1),
        (x + 1, y),
        (x, y + 1),
      ] if adjacents else []),
      *([
        (x - 1, y - 1),
        (x + 1, y - 1),
        (x - 1, y + 1),
        (x + 1, y + 1),
      ] if diagonals else [])
    ]
    return (neighbors
      if not predicate
      else [n for n in neighbors if predicate(n)])

  cells = []
  start = cell
  if inclusive:
    cells.append(start)

  stack = [(start, 0)]
  while stack:
    cell, steps = stack.pop()
    neighbors = neighborhood(cell, adjacents=adjacents, diagonals=diagonals)
    for neighbor in neighbors:
      if neighbor not in cells and neighbor != start and (not predicate or predicate(neighbor)):
        cells.append(neighbor)
        if steps + 1 < radius:
          stack.append((neighbor, steps + 1))

  return cells
