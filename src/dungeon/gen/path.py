from random import randint

def gen_path(start, goal, delta=False, predicate=None, attempts=256):
  path = [start]
  cell = start
  goal_x, goal_y = goal
  delta_x, delta_y = delta or (0, 0)
  while cell != goal and attempts:
    x, y = cell
    dist_x = goal_x - x
    dist_y = goal_y - y
    if delta:
      if dist_x and delta_x:
        delta_x = dist_x / abs(dist_x)
        delta_y = 0
      elif dist_y and delta_y:
        delta_x = 0
        delta_y = dist_y / abs(dist_y)
      elif dist_x:
        delta_x = dist_x / abs(dist_x)
        delta_y = 0
      elif dist_y:
        delta_x = 0
        delta_y = dist_y / abs(dist_y)
    else:
      if dist_x and dist_y:
        if randint(0, 1):
          delta_x = dist_x / abs(dist_x)
        else:
          delta_y = dist_y / abs(dist_y)
      elif dist_x:
        delta_x = dist_x / abs(dist_x)
      else:
        delta_y = dist_y / abs(dist_y)
    x += delta_x
    y += delta_y
    next_cell = (int(x), int(y))
    if predicate and not predicate(next_cell):
      attempts -= 1
      continue
    cell = next_cell
    path.append(cell)
  return path if cell == goal else []
