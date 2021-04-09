import random
from grid import Grid

def equals(a, b):
  return a[0] == b[0] and a[1] == b[1]

def default():
  grid = Grid((11, 11))
  grid.data = [
    1, 1, 1, 1, 1, 1, 1, 1, 1,
    1, 1, 1, 1, 1, 1, 1, 1, 1,
    1, 0, 0, 0, 0, 0, 0, 0, 1,
    1, 0, 0, 0, 0, 0, 1, 0, 1,
    1, 0, 0, 0, 0, 0, 1, 0, 1,
    1, 0, 0, 0, 0, 0, 0, 0, 1,
    1, 0, 0, 0, 0, 0, 0, 0, 1,
    1, 0, 0, 0, 0, 0, 0, 0, 1,
    1, 1, 1, 1, 1, 1, 1, 1, 1,
  ]

def maze(width, height):
  grid = Grid((width, height))
  grid.fill(1)
  x = (random.randrange(0, width // 2) + 1) * 2 - 1
  y = (random.randrange(0, height // 2) + 1) * 2 - 1
  start = (x, y)
  node = start
  stack = [start]
  visited = [start]
  while node:
    grid.set_at(node, 0)
    (x, y) = node
    neighbors = [
      (x - 2, y),
      (x + 2, y),
      (x, y - 2),
      (x, y + 2)
    ]
    random.shuffle(neighbors)
    for neighbor in neighbors:
      if not grid.contains(neighbor):
        continue
      for node in visited:
        if equals(node, neighbor):
          break
      else:
        (neighbor_x, neighbor_y) = neighbor
        midpoint = ((x + neighbor_x) // 2, (y + neighbor_y) // 2)
        grid.set_at(midpoint, 0)
        stack.append(neighbor)
        visited.append(neighbor)
        node = neighbor
        break
    else:
      if len(stack) > 1:
        stack.pop()
        node = stack[len(stack) - 1]
      else:
        node = None
  return grid
