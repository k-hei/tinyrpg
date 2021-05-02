def manhattan(a, b):
  x1, y1 = a
  x2, y2 = b
  return abs(x2 - x1) + abs(y2 - y1)

def is_adjacent(a, b):
  return manhattan(a, b) == 1

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

def is_odd(cell):
  x, y = cell
  return x % 2 == 1 and y % 2 == 1

def neighbors(cell):
  x, y = cell
  return [
    (x - 1, y),
    (x, y - 1),
    (x + 1, y),
    (x, y + 1)
  ]
