def invert(direction):
  dir_x, dir_y = direction
  return (-dir_x, -dir_y)

def normalize(direction):
  dir_x, dir_y = direction
  return (abs(dir_x), abs(dir_y))

def normal(direction):
  dir_x, dir_y = direction

  if dir_x < 0:
    dir_x = -1
  elif dir_x > 0:
    dir_x = 1

  if dir_y < 0:
    dir_y = -1
  elif dir_y > 0:
    dir_y = 1

  return (dir_x, dir_y)
