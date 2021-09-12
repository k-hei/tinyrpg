from random import randint

def gen_path(start, goal, predicate=None, attempts=256):
  path = [start]
  cell = start
  goal_x, goal_y = goal
  while cell != goal and attempts:
    x, y = cell
    dist_x = goal_x - x
    dist_y = goal_y - y
    if dist_x and dist_y:
      if randint(0, 1):
        x += dist_x / abs(dist_x)
      else:
        y += dist_y / abs(dist_y)
    elif dist_x:
      x += dist_x / abs(dist_x)
    else:
      y += dist_y / abs(dist_y)
    next_cell = (int(x), int(y))
    if predicate and not predicate(next_cell):
      attempts -= 1
      continue
    cell = next_cell
    path.append(cell)
  return path if cell == goal else []
