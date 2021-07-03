def invert(direction):
  dir_x, dir_y = direction
  return (-dir_x, -dir_y)

def normalize(direction):
  dir_x, dir_y = direction
  return (abs(dir_x), abs(dir_y))
